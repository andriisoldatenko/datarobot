Homework Assignment: Today's Weather
====================================

The program should retrieve and display current weather conditions,
using a supplied IP address to look up the location data. If no address
is provided, use the user's public IP address. It should have a CLI, with
any flags and parameters deemed appropriate. It should be a tool that
others can easily use and modify.

The program should be written in Python, and should run on Python 2.7.3.
You may use third party libraries from PyPI, but if so you must include
a `requirements.txt` file.


### How to use
#### Install requirements

```
pip install -r requirements.txt
```

#### Run weather now
```
python weather.py -h
```

#### or with ip address
```
python weather.py -ip 17.0.0.0
```