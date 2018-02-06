import datetime
from functools import reduce
from time import gmtime, strftime

import requests
import tweepy

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
