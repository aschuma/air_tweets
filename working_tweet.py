import datetime
import sys
from functools import reduce
from io import StringIO
from io import BytesIO

import jsonpath_rw_ext as jp
import requests
import tweepy
from twython import Twython

from config import *

graphPM100 = BytesIO(requests.get(conf_luftdaten_graph_pm100_url).content)
graphPM025 = BytesIO(requests.get(conf_luftdaten_graph_pm025_url).content)

print(graphPM025)
print(graphPM100)

url_pm_sensor = conf_luftdaten_url % conf_particle_sensor_id
url_th_sensor = conf_luftdaten_url % conf_temperature_sensor_id

url_pm_sensor = "http://api.luftdaten.info/static/v2/data.1h.json"
url_th_sensor = "http://api.luftdaten.info/static/v2/data.1h.json"

print(url_pm_sensor)
print(url_th_sensor)

json_pm = requests.get(url_pm_sensor).json()
json_th = requests.get(url_th_sensor).json()

item_pm = [item for item in json_pm if item['sensor']['id'] == conf_particle_sensor_id][-1]
item_th = [item for item in json_th if item['sensor']['id'] == conf_temperature_sensor_id][-1]


def extract_value_from_json(json, key):
    query = '$.sensordatavalues[?(value_type="{}")].value'.format(key)
    matches = jp.match(query, json)
    return float(matches[-1])


value_pm100 = extract_value_from_json(item_pm, "P1")
value_pm025 = extract_value_from_json(item_pm, "P2")
value_temperature = extract_value_from_json(item_th, "temperature")
value_humidity = extract_value_from_json(item_th, "humidity")


print([value_pm100,value_pm025,value_temperature,value_humidity])


if value_pm100 <= 10:
    sys.exit(0)


twitter = Twython(consumer_key, consumer_secret, access_token, access_token_secret)
twitter.verify_credentials()


response_graphPM100 = twitter.upload_media(media=graphPM100)
print(response_graphPM100)
response_graphPM025 = twitter.upload_media(media=graphPM025)
print(response_graphPM025)



twitter.update_status(status='TEST UPLOAD', media_ids=[response_graphPM100['media_id'],response_graphPM025['media_id']])

print([value_pm100,value_pm025,value_temperature,value_humidity])
sys.exit(0)

def lookup_sensors(base_url, sensors):
    def lookup_single_sensor_data(url_param):

        response = requests.get(url_param)

        print(response.json())

        if response.ok:
            data_records = response.json()
            current_data_record = data_records[-1]
            v1 = current_data_record['sensordatavalues'][0]['value']
            v2 = current_data_record['sensordatavalues'][-1]['value']
            return v1, v2
        else:
            return None, None

    return map(lookup_single_sensor_data, map(lambda sensor_id: base_url % sensor_id, sensors))


def lookup():
    (pm_10_0_p, pm_2_50_p), (temperature_p, humidity_p) = lookup_sensors(
        conf_luftdaten_url,
        [conf_particle_sensor_id, conf_temperature_sensor_id])

    if reduce(lambda zero, item: zero and item is not None, [pm_10_0_p, pm_2_50_p, temperature_p, humidity_p], True):
        return [pm_10_0_p, pm_2_50_p, temperature_p, humidity_p]
    else:
        return None




def twitter_api():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def tweet(msg):
    try:
        twitter_api().update_status(msg)
    except tweepy.TweepError as e:
        print(e.reason)


def last_bot_tweets():
    def print_last_tweets(timeline_filtered):
        print("--- last tweets ----")
        for item in timeline_filtered:
            print(item)
        print("--------------------")

    def has_bot_marker(timeline_item):
        hashtags = [tags['text'] for tags in timeline_item.entities['hashtags']]
        return conf_twitter_tag_bot in hashtags

    try:
        timeline = twitter_api().user_timeline(user_id=conf_twitter_user_id, count=50)
        timeline_filtered = [item for item in timeline if has_bot_marker(item)]

        print_last_tweets(timeline_filtered)

        return timeline_filtered

    except tweepy.TweepError as e:
        print(e.reason)


def may_tweet_again():
    reference_timestamp = datetime.datetime.now() - datetime.timedelta(hours=conf_quiet_period_in_hours)
    tweet_ts = [item.created_at for item in last_bot_tweets()]
    allowed = len(tweet_ts) == 0 or max(tweet_ts) < reference_timestamp

    print("may_tweet_again reference={}, tweets_ts{} -> {}".format( reference_timestamp, [str(item) for item in tweet_ts], allowed))

    return allowed


pm_10_0, pm_2_50, temperature, humidity = lookup()

if pm_10_0 is not None and pm_2_50 is not None and float(pm_10_0) > conf_limit_pm_10_0:
    current_time = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())

    message = "{} #{}\n⚠ PM10: {}µg/m³, PM2.5: {}µg/m³, {}°C, RH:{}%\nDetails: {}\nThis is a bot, code available on github aschuma/air_tweets\n".format(
        conf_twitter_msg_preamble,
        conf_twitter_tag_bot,
        pm_10_0,
        pm_2_50,
        temperature,
        humidity,
        conf_luftdaten_map_url
    )

    print(message)

    if may_tweet_again():
        tweet(message)
