import datetime
import shelve
import sys
from time import strftime
import jsonpath_rw_ext as jp
import requests
from jinja2 import Template
from bluesky_send_post import send_bluesky_post
from env import load_configuration
from mastodon_send_post import send_mastodon_post

# Load configuration
config = load_configuration()

def sensor_json(url):
    return requests.get(url).json()

def sensor_item(sensor_json_list, sensor_id):
    return [item for item in sensor_json_list if item['sensor']['id'] == sensor_id][-1]

def extract_value_from_json_item(json, key):
    query = '$.sensordatavalues[?(value_type="{}")].value'.format(key)
    matches = jp.match(query, json)
    return float(matches[-1])

def read_last_tweet_ts():
    db = shelve.open(config['conf_storage'])
    if not 'tweet_ts' in db:
        db['tweet_ts'] = datetime.datetime(year=1970, month=1, day=1)
    tweet_ts = db['tweet_ts']
    db.close()
    return tweet_ts

def write_last_tweet_ts(tweet_ts):
    db = shelve.open(config['conf_storage'])
    db['tweet_ts'] = tweet_ts
    db.close()

def quiet_period_exceeded():
    return datetime.datetime.now() - datetime.timedelta(hours=config['conf_quiet_period_in_hours']) > read_last_tweet_ts()

def update_quiet_period():
    write_last_tweet_ts(datetime.datetime.now())

def render_template(template_str, params):
    template = Template(template_str)
    return template.render(params)

if not quiet_period_exceeded():
    print("noop, within quiet period")
    sys.exit(0)

pm_sensor_item = sensor_item(
    sensor_json(config['conf_url_pm_sensor']),
    config['conf_particle_sensor_id'])

th_sensor_item = sensor_item(
    sensor_json(config['conf_url_th_sensor']),
    config['conf_temperature_sensor_id']) if config['conf_temperature_sensor_id'] is not None else None

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
    'luftdaten_map_url': config['conf_luftdaten_map_url']
}

if value_pm100 < config['conf_limit_pm_10_0']:
    print("noop, limit not exceeded, current=",
          value_pm100, " limit=", config['conf_limit_pm_10_0'])
    sys.exit(0)

image_bytes = requests.get(config['conf_luftdaten_graph_url'].format(
    config['conf_particle_sensor_id'])).content

mastodon_jinja2_template = config['conf_mastodon_template']
bluesky_jinja2_template = config['conf_bluesky_template']
mastodon_enabled = config['conf_mastodon_enabled']
bluesky_enabled = config['conf_bluesky_enabled']

message_mastodon = render_template(mastodon_jinja2_template, template_params)
message_bluesky = render_template(bluesky_jinja2_template, template_params)
print("\nmastodon:\n|", message_mastodon, "|")
print("\nbluesky:\n|", message_bluesky, "|")

if mastodon_enabled:
    send_mastodon_post(config, message_mastodon, image_bytes)
    print("Mastodon: Done")

if bluesky_enabled:
    send_bluesky_post(config, message_bluesky, image_bytes)
    print("Bluesky: Done")

update_quiet_period()

print("Done")
