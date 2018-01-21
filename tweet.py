import json
import tweepy
import requests
from functools import reduce
from time import gmtime, strftime
from config import *


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
        luftdaten_url,
        [particle_sensor_id, temperature_sensor_id])

    if reduce(lambda zero, item: zero and item is not None, [pm_10_0_p, pm_2_50_p, temperature_p, humidity_p], True):
        return [pm_10_0_p, pm_2_50_p, temperature_p, humidity_p]
    else:
        return None


def tweet(msg):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    try:
        api.update_status(msg)
    except tweepy.TweepError as e:
        print(e.reason)


pm_10_0, pm_2_50, temperature, humidity = lookup()


if pm_10_0 is not None and pm_2_50 is not None and float(pm_10_0) > limit_pm_10_0:

    current_time = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime())

    message = "{}\nCurrent values: PM10: {}g/m³ PM2.5: {}µg/m³\n{}".format(
        twitter_tags,
        pm_10_0,
        pm_2_50,
        luftdaten_map_url
    )

    print(message)

    tweet(message)





