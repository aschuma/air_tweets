import datetime
import shelve
import sys
from io import BytesIO
from time import strftime
from mastodon import Mastodon
import jsonpath_rw_ext as jp
import requests
from jinja2 import Template
from atproto import Client
import re

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


def render_template(template_str, params):
    template = Template(template_str)
    text = template.render(params)
    lines = text.split('\n')
    preserved_lines = [line if line.strip() else ' ' for line in lines]
    return '\n'.join(preserved_lines).rstrip()

def add_bluesky_facets(text):
    """
    Generates facets for hashtags in the given text, ignoring hashtags within URLs.
    """
    facets = []

    # Regex pattern for URLs
    url_pattern = r"https?://[^\s]+"
    # Regex pattern for hashtags
    hashtag_pattern = r"#(\w+)"

    # Find all URLs in the text and their positions
    url_matches = [(match.start(), match.end()) for match in re.finditer(url_pattern, text)]

    # Find hashtags and create facets, ensuring they are not part of a URL
    for match in re.finditer(hashtag_pattern, text):
        start, end = match.span()
        # Check if the hashtag is within any URL
        is_inside_url = any(start >= url_start and end <= url_end for url_start, url_end in url_matches)
        if not is_inside_url:
            facets.append({
                "index": {
                    "byteStart": start,
                    "byteEnd": end,
                },
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#tag",
                        "tag": match.group(1),  # The tag without the #
                    }
                ],
            })

    return facets


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

current_timestamp = strftime("%d.%m.%Y %H:%M") + " CET"
template_params = {
    'pm10': value_pm100,
    'pm25': value_pm025,
    'temperature': value_temperature,
    'humidity': value_humidity,
    'current_time': current_timestamp,
    'luftdaten_map_url': conf_luftdaten_map_url
}

if value_pm100 < conf_limit_pm_10_0:
    print("noop, limit not exceeded, current=",
          value_pm100, " limit=", conf_limit_pm_10_0)
    sys.exit(0)

image_bytes = requests.get(
    conf_luftdaten_graph_url).content if conf_luftdaten_graph_url else None

message_mastodon = render_template(mastodon_jinja2_template, template_params)
message_bluesky = render_template(bluesky_jinja2_template, template_params)
print("\nmastodon:\n", message_mastodon)
print("\nbluesky:\n", message_bluesky)


if mastodon_enabled:
    mastodon = Mastodon(
        access_token=mastodon_access_token,
        api_base_url=mastodon_api_base_url)
    if image_bytes:
        mastodon_upload_response = mastodon.media_post(
            media_file=BytesIO(image_bytes),
            mime_type=conf_luftdaten_graph_mime_type)
        mastodon.status_post(
            status=message_mastodon,
            media_ids=[mastodon_upload_response])
    else:
        mastodon.status_post(
            status=message_mastodon)
    print("Mastodon: Done")

if bluesky_enabled:
    client = Client()
    client.login(bluesky_handle, bluesky_password)
    facets = add_bluesky_facets(message_bluesky)
    if image_bytes:
        client.send_image(text=message_bluesky, image=BytesIO(image_bytes), image_alt='PM10 graph ' + current_timestamp, facets=facets)
    else:
        client.send_post(text=message_bluesky, facets=facets)
    print("Bluesky: Done")

update_quiet_period()

print("Done")
