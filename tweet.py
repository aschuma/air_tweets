import datetime
import shelve
import sys
from io import BytesIO
from time import strftime
from mastodon import Mastodon
import jsonpath_rw_ext as jp
import requests
from jinja2 import Template

from config import *


def sensor_json(url):
    return requests.get(url).json()


def sensor_item(sensor_json_list, sensor_id):
    return [item for item in sensor_json_list if item['sensor']['id'] == sensor_id][-1]


def extract_value_from_json_item(json, key):
    query = '$.sensordatavalues[?(value_type="{}")].value'.format(key)
    matches = jp.match(query, json)
    return float(matches[-1])


def read_last_tweet_ts():
    db = shelve.open(conf_storage)
    if not 'tweet_ts' in db:
        db['tweet_ts'] = datetime.datetime(year=1970, month=1, day=1)
    tweet_ts = db['tweet_ts']
    db.close()
    return tweet_ts


def write_last_tweet_ts(tweet_ts):
    db = shelve.open(conf_storage)
    db['tweet_ts'] = tweet_ts
    db.close()


def quiet_period_exceeded():
    return datetime.datetime.now() - datetime.timedelta(hours=conf_quiet_period_in_hours) > read_last_tweet_ts()


def update_quiet_period():
    write_last_tweet_ts(datetime.datetime.now())


def preserve_multiline_text(text):
    lines = text.split('\n')
    preserved_lines = [line if line.strip() else ' ' for line in lines]
    preserved_text = '\n'.join(preserved_lines).rstrip()
    return preserved_text


if not quiet_period_exceeded():
    print("noop, within quiet period")
    sys.exit(0)

pm_sensor_item = sensor_item(
    sensor_json(conf_url_pm_sensor),
    conf_particle_sensor_id)

th_sensor_item = sensor_item(
    sensor_json(conf_url_th_sensor),
    conf_temperature_sensor_id) if conf_temperature_sensor_id is not None else None

value_pm100 = extract_value_from_json_item(pm_sensor_item, "P1")
value_pm025 = extract_value_from_json_item(pm_sensor_item, "P2")
value_temperature = extract_value_from_json_item(
    th_sensor_item, "temperature") if th_sensor_item else None
value_humidity = extract_value_from_json_item(
    th_sensor_item, "humidity") if th_sensor_item else None

print([value_pm100, value_pm025, value_temperature, value_humidity])

current_time = strftime("%d.%m.%Y %H:%M:%S")

template = Template(conf_jinja2_template)

message = preserve_multiline_text(template.render(
    pm10=value_pm100,
    pm25=value_pm025,
    temperature=value_temperature,
    humidity=value_humidity,
    current_time=current_time,
    luftdaten_map_url=conf_luftdaten_map_url
))

print(message)

if value_pm100 < conf_limit_pm_10_0:
    print("noop, limit not exceeded, current=",
          value_pm100, " limit=", conf_limit_pm_10_0)
    sys.exit(0)

image_bytes = requests.get(
    conf_luftdaten_graph_url).content if conf_luftdaten_graph_url else None

if mastodon_enabled:
    mastodon = Mastodon(
        access_token=mastodon_access_token,
        api_base_url=mastodon_api_base_url)
    if image_bytes:
        mastodon_upload_response = mastodon.media_post(
            media_file=BytesIO(image_bytes),
            mime_type=conf_luftdaten_graph_mime_type)
        mastodon.status_post(
            status=message,
            media_ids=[mastodon_upload_response])
    else:
        mastodon.status_post(
            status=message)
    print("Mastodon: Done")

update_quiet_period()

print("Done")
