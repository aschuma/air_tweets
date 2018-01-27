```
  :::.       :::  :::::::..     ::::::::::::.::    .   .:::.,:::::: .,:::::::::::::::::: .::::::. 
  ;;`;;      ;;;  ;;;;``;;;;    ;;;;;;;;''''';;,  ;;  ;;;' ;;;;'''' ;;;;'''';;;;;;;;'''';;;`    ` 
 ,[[ '[[,    [[[   [[[,/[[['         [[      '[[, [[, [['   [[cccc   [[cccc      [[     '[==/[[[[,
c$$$cc$$$c   $$$   $$$$$$c           $$        Y$c$$$c$P    $$""""   $$""""      $$       '''    $
 888   888,  888   888b "88bo,       88,        "88"888     888oo,__ 888oo,__    88,     88b    dP
 YMM   ""`   MMM   MMMM   "W"        MMM         "M "M"     """"YUMMM""""YUMMM   MMM      "YMmMY"                                         
 
```
# Tweeters air quality measurement results of feinstaub sensors (http://luftdaten.info)


## config

Set your Twitter credentials in config.py.
Set your sensor meta data in config.py.

(see config.py-template for example)

## run as cron

add to your crontab:

```
20 0 * * * cd /home/myuser/myproject && venv/bin/python tweet.py > /dev/null 2>&1
```

## virtualenv

```
cp config.py-template config.py
# edit config.py
virtualenv venv -p /usr/bin/python3
source venv/bin/activate
pip3 install -r requirements.txt
python tweet.py

```

