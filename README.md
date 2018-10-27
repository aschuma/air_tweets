```
  :::.       :::  :::::::..     ::::::::::::.::    .   .:::.,:::::: .,:::::::::::::::::: .::::::. 
  ;;`;;      ;;;  ;;;;``;;;;    ;;;;;;;;''''';;,  ;;  ;;;' ;;;;'''' ;;;;'''';;;;;;;;'''';;;`    ` 
 ,[[ '[[,    [[[   [[[,/[[['         [[      '[[, [[, [['   [[cccc   [[cccc      [[     '[==/[[[[,
c$$$cc$$$c   $$$   $$$$$$c           $$        Y$c$$$c$P    $$""""   $$""""      $$       '''    $
 888   888,  888   888b "88bo,       88,        "88"888     888oo,__ 888oo,__    88,     88b    dP
 YMM   ""`   MMM   MMMM   "W"        MMM         "M "M"     """"YUMMM""""YUMMM   MMM      "YMmMY"                                         
 
```
# Tweets air quality measurement results of particulate matter (Feinstaub) (http://luftdaten.info)

This is the source code of a Twitter bot that monitors particulate matter (Feinstaub) for a single 
sensor of the http://luftdaten.info network. A tweet is published in case the PM10 particulate matter 
exceeds a configurable value, e.g. 50 µg/m³.

A tweet might look like this:

<img width="482" height="388" src="https://github.com/aschuma/air_tweets/raw/master/tweet-screnshot.png">

This repository provides a cron job written in python 3. After a tweet submission no further tweets
are created for a configurable period. 

# Installation

- Create a twitter account, obtain an access token, see https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens for further details.
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
   
   # the sensor ids
   conf_particle_sensor_id = 6655
   conf_temperature_sensor_id = 6656
   
   # url used to fetch the avg sensor of the last hour
   conf_url_pm_sensor = "http://api.luftdaten.info/static/v2/data.1h.json"
   conf_url_th_sensor = "http://api.luftdaten.info/static/v2/data.1h.json"
   
   # sensor graphs to embed in the tweet
   conf_luftdaten_graph_pm100_url = "https://www.madavi.de/sensor/images/sensor-esp8266-532353-sds011-1-day.png"
   conf_luftdaten_graph_pm025_url = "https://www.madavi.de/sensor/images/sensor-esp8266-532353-sds011-25-day.png"
   
   # PM 10 limit
   conf_limit_pm_10_0 = 50
   
   # quiet period after after a tweet has published
   conf_quiet_period_in_hours = 6
   
   # stuff to embed in the tweet
   conf_luftdaten_map_url = "http://deutschland.maps.luftdaten.info/#13/48.8066/9.2372"
   conf_twitter_msg_preamble = "#feinstaub #feinstaubalarm #cannstatt"
   
   # Credentials provided by twitter
   consumer_key = ''
   consumer_secret = ''
   access_token = ''
   access_token_secret = ''
    
   ```
- Setup a cron job

  ```
  */15 * * * * cd /home/pi/projects/air_tweets && venv/bin/python tweet.py > /dev/null 2>&1
  ```

# Contribution
Please feel free to issue a bug report or submit a PR. Any helping hand is welcome. 

Be aware that my primary coding language is Java. So currently some code portions might not follow python best practices.
