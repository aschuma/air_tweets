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
 ```
#feinstaub #feinstaubalarm  #bot
⚠ PM10: 68.07g/m,³ PM2.5: 41.87µg/m³, 5.50°C, RH:96.00%
http://deutschland.maps.luftdaten.info/#13/48.8066/9.2372
```

This repository provides a cron job written in python 3. After a tweet submission no further tweets
are created for a configurable period. 


# Installation

- Create a twitter account, obtain an access token, see https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens for further details.
- Make sure python 3 is installed on your dev machine.
- Clone this repository
- Create a virtual environment, e.g. you may obtain more information about those steps here: http://docs.python-guide.org/en/latest/dev/virtualenvs/ 
 ```
   virtualenv venv -p /usr/bin/python3
   source venv/bin/activate
   pip3 install -r requirements.txt 
 ```
- Copy the file ```config.py-template``` to ```config.py```, adjust the setup. At least you should alter the following values as starting point.

```
   # Your PM sensor ID
   conf_particle_sensor_id = 4711
   # Your temperature sensor ID
   conf_temperature_sensor_id = 4711
   # The URL pointing to the location of your sensor
   conf_luftdaten_map_url = "http://deutschland.maps.luftdaten.info/#13/48.8066/9.2372"
   # The name of your twitter account
   conf_twitter_user_id = 'my-account'

   # Credentials provided by twitter
   consumer_key = ''
   consumer_secret = ''
   access_token = ''
   access_token_secret = ''
 
```
- Setup a cron job

```
*/15 * * * * cd /home/pi/projects/aschuma__luftdaten_tweet && venv/bin/python tweet.py > /dev/null 2>&1
```

# Contribution
Please feel free to issue a bug report or create a PR. Any helping hand is welcome. 

Be aware that my primary coding language is Java. So currently some code portions might not follow python best practices.
