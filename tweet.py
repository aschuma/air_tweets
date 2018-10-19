import datetime
import shelve
import sys
from io import BytesIO
from time import strftime
from time import time
from twython import Twython
import jsonpath_rw_ext as jp
import requests

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


if not quiet_period_exceeded():
    print("noop, within quiet period")
    sys.exit(0)

pm_sensor_item = sensor_item(
    sensor_json(conf_url_pm_sensor),
    conf_particle_sensor_id)

th_sensor_item = sensor_item(
    sensor_json(conf_url_th_sensor),
    conf_temperature_sensor_id)

value_pm100 = extract_value_from_json_item(pm_sensor_item, "P1")
value_pm025 = extract_value_from_json_item(pm_sensor_item, "P2")
value_temperature = extract_value_from_json_item(th_sensor_item, "temperature")
value_humidity = extract_value_from_json_item(th_sensor_item, "humidity")

print([value_pm100, value_pm025, value_temperature, value_humidity])

current_time = strftime("%d.%m.%Y %H:%M:%S")

# ⚠ PM10: {}µg/m³, PM2.5: {}µg/m³, {}°C, RH:{}% ({})
message = '''
{}
⚠ PM10: {}µg/m³, PM2.5: {}µg/m³, {}°C ({})
Details: {}
#bot code: github aschuma/air_tweets
'''.format(
    conf_twitter_msg_preamble,
    value_pm100,
    value_pm025,
    value_temperature,
#    value_humidity,
    current_time,
    conf_luftdaten_map_url
)

print(message)

if value_pm100 < conf_limit_pm_10_0:
    print("noop, limit not exceeded, current=", value_pm100, " limit=", conf_limit_pm_10_0)
    sys.exit(0)

to_time = int(round(time() * 1000))
from_time = to_time - (1000*60*60*24)

url_PM100 = conf_luftdaten_graph_pm100_url.format(from_time, to_time)
url_PM025 = conf_luftdaten_graph_pm025_url.format(from_time, to_time)
print(url_PM100)
print(url_PM025)

graphPM100 = BytesIO(requests.get(url_PM100).content)
#graphPM025 = BytesIO(requests.get(url_PM025).content)

twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
twitter.verify_credentials()

response_graphPM100 = twitter.upload_media(media=graphPM100)
#response_graphPM025 = twitter.upload_media(media=graphPM025)
twitter.update_status(status=message,
                      media_ids=[
                          response_graphPM100['media_id']
                      #    , response_graphPM025['media_id']
                      ])

update_quiet_period()

print("Done")
