```
  :::.       :::  :::::::..     ::::::::::::.::    .   .:::.,:::::: .,:::::::::::::::::: .::::::. 
  ;;`;;      ;;;  ;;;;``;;;;    ;;;;;;;;''''';;,  ;;  ;;;' ;;;;'''' ;;;;'''';;;;;;;;'''';;;`    ` 
 ,[[ '[[,    [[[   [[[,/[[['         [[      '[[, [[, [['   [[cccc   [[cccc      [[     '[==/[[[[,
c$$$cc$$$c   $$$   $$$$$$c           $$        Y$c$$$c$P    $$""""   $$""""      $$       '''    $
 888   888,  888   888b "88bo,       88,        "88"888     888oo,__ 888oo,__    88,     88b    dP
 YMM   ""`   MMM   MMMM   "W"        MMM         "M "M"     """"YUMMM""""YUMMM   MMM      "YMmMY"                                         
 
```
# Tweets air quality measurement results of particulate matter (Feinstaub) (http://luftdaten.info)

This source code is for a Mastodon / Bluesky bot that monitors particulate matter (Feinstaub) for a single sensor from the https://sensor.community network. The bot will automatically publish a tweet when the PM10 particulate matter exceeds a configurable threshold, such as 50 µg/m³."

A tweet might look like this:

<img width="482" height="388" src="https://github.com/aschuma/air_tweets/raw/main/tweet-screnshot.png">

This repository provides a cron job written in python 3. After a tweet submission no further tweets
are created for a configurable period.

# Installation

- Create a Mastodont account, obtain an access token, see https://docs.joinmastodon.org/client/token for further details.
- Make sure python 3 is installed on your dev machine.
- Clone this repository
- Create a virtual environment, you may obtain more information about the steps below here: http://docs.python-guide.org/en/latest/dev/virtualenvs/ 
   ```
   virtualenv venv -p /usr/bin/python3
   source venv/bin/activate
   pip3 install -r requirements.txt 
   ```
   
- Copy the file ```config.py-template``` to ```config.py```, adjust the setup. At least you should alter the following values as starting point.

   ```
  # database, last tweet timestamp
  conf_storage = "/tmp/.air_tweet"

  # the sensor IDs (temperature is optional. If you provide an ID, consider updating the templates accordingly)
  conf_particle_sensor_id = 90887
  conf_temperature_sensor_id = None

  # url used to fetch the avg sensor of the last hour
  [..]

  # sensor graph grafana image to embed in the tweet (optional)
  #   conf_luftdaten_graph_url = "http://192.168.0.43:3000/render/d-solo/eDF152mRk/twitter?panelId=2&orgId=1&from={}&to={}&width=800&height=500&tz=UTC%2B02%3A00"
  conf_luftdaten_graph_url = None
  conf_luftdaten_graph_mime_type = "image/png"

  # PM 10 limit
  conf_limit_pm_10_0 = 50

  # stuff to embed in the tweet - link to sensor community map
  conf_luftdaten_map_url = "https://maps.sensor.community/#15/48.8040/9.2280"

  # quiet period after a tweet has been published
  conf_quiet_period_in_hours = 6

  # mastodon credentials
  mastodon_enabled = True
  mastodon_api_base_url = 'https://mastodon.online' 
  mastodon_access_token =  ''

  # bluesky credentials
  bluesky_enabled = False
  bluesky_handle = '....bsky.social'
  bluesky_password = '...'

  [..]
   ```

- Setup a cron job

  ```
  */15 * * * * cd /home/pi/projects/air_tweets && venv/bin/python tweet.py > /dev/null 2>&1
  ```

# Contribution

Please feel free to issue a bug report or submit a PR. Any helping hand is welcome. 

Be aware that my primary coding language is Java. So currently some code portions might not follow python best practices.


