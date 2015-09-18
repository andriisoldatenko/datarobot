#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Display current weather conditions,
using a supplied IP address to look up the location data. If no address
is provided, use the user's public IP address. It should have a CLI, with
any flags and parameters deemed appropriate. It should be a tool that
others can easily use and modify.
"""

import argparse
import re
import sys
from collections import defaultdict

import requests
from clint.textui import colored, puts
from geoip import geolite2

SUN = u'\u2600'
CLOUDS = u'\u2601'
RAIN = u'\u2602'
SNOW = u'\u2603'

IPV4_RE = re.compile(r'^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|'
                     r'[0-1]?\d?\d)){3}$')


class TextFormatter(object):
    """
    Simple text formatter string
    """
    @staticmethod
    def output(context):
        """
        Get context and return formatted output
        :param context:
        :return:
        """
        return u"Today it's {0}\u00B0 {1} and {2}".format(
            context['temp'],
            context['icon'],
            context['conditions'].lower()
        )


class WeatherDataException(Exception):
    """The requested weather data does not exist"""
    pass


class IPAddressException(Exception):
    """Invalid IPv4 address."""
    pass


def get_temperature_color(conditions):
    """
    Get color based on temperature
    """
    temp_color_map = [
        (40, 'cyan'),
        (60, 'blue'),
        (80, 'yellow')
    ]

    temperature_re = re.compile(r'(?P<temperature>-?\d+)')
    match = temperature_re.search(conditions)
    if match:
        for color in temp_color_map:
            if int(match.group('temperature')) <= color[0]:
                return color[1]
        return 'red'
    return 'white'


class OpenWeatherMap(object):
    """
    Open weather map current weather and forecast
    based on http://openweathermap.org/api
    """
    url = 'http://api.openweathermap.org/data/2.5/weather'

    MAPPING_UNITS = {'fahrenheit': 'imperial', 'celsius': 'metric'}

    def __init__(self, formatter=TextFormatter()):
        self.formatter = formatter

    def now(self, lat=0, lon=0, units='fahrenheit'):
        """
        Create get request to Open weather map
        """
        payload = {'lat': lat, 'lon': lon, 'units': self.MAPPING_UNITS[units]}
        response = requests.get(self.url, params=payload)

        try:
            weather = response.json()
        except ValueError:
            raise WeatherDataException("Incorrect json response")

        context = {}
        try:
            context['temp'] = int(weather['main']['temp'])
            context['conditions'] = weather['weather'][0]['description']
            context['icon'] = OpenWeatherMap.ascii_icon(weather['weather'][0]['icon'])
        except KeyError:
            raise WeatherDataException("No conditions reported for your "
                                       "search")

        return self.formatter.output(context)

    @staticmethod
    def ascii_icon(code):
        """
        Mapping between open weather map codes and weather icons
        """
        codes = defaultdict(int, {
            '01d': SUN,
            '01n': SUN,
            '02d': CLOUDS,
            '02n': CLOUDS,
            '03d': CLOUDS,
            '03n': CLOUDS,
            '04d': CLOUDS,
            '04n': CLOUDS,
            '09d': RAIN,
            '09n': RAIN,
            '10d': RAIN,
            '10n': RAIN,
            '11d': RAIN,
            '11n': RAIN,
            '13d': SNOW,
            '13n': SNOW,
        })
        return codes[code]


class PublicIPAddress(object):
    """
    Resolve Public IPAddress using 3rd party service
    """
    def __init__(self, url='http://ip.42.pl/raw'):
        self.url = url

    def resolve(self):
        """
        http://stackoverflow.com/questions/9481419/how-can-i-get-the-public-ip-using-python2-7
        """
        resp = requests.get(self.url)
        if self.validate(resp.text):
            return resp.text

    @staticmethod
    def validate(ip_address):
        """
        Validate ip v4 address
        """
        if not IPV4_RE.match(ip_address):
            raise IPAddressException('Incorrect ip v4 '
                                     'address {}'.format(ip_address))
        return True


class Arguments(object):
    """
    Parse arguments
    """

    def __init__(self):
        self.units = ('celsius', 'fahrenheit')

        self.parser = argparse.ArgumentParser(
            description="Outputs the weather for a given ip address or "
                        "public ip address otherwise.")
        self.parser.add_argument('-u', '--units', dest='units',
                                 choices=self.units,
                                 default=self.units[1],
                                 help="Units of measurement "
                                      "(default: fahrenheit)")

        self.parser.add_argument('-ip', '--ip-address', dest='ip_address',
                                 help="Provide IP Address V4")

    def parse(self, args):
        """
        :param args:
        :return:
        """
        args = self.parser.parse_args(args)
        return {
            'ip': args.ip_address,
            'units': args.units
        }


class Weather(object):
    """
    Retrieve and display current weather conditions based on current location
    or --ip-address cli parameter with pretty output with icons and colors
    """
    @staticmethod
    def run():
        """
        Run the main program
        """
        arguments = Arguments()
        args = arguments.parse(sys.argv[1:])

        formatter = TextFormatter()

        if not args['ip']:
            # Lookup my ip_address
            # but Armin hardcoded url for checking ip address :)
            # ip_address = geolite2.lookup_mine()
            ip_address = PublicIPAddress().resolve()
        else:
            ip_address = args['ip']
            PublicIPAddress().validate(ip_address)

        match = geolite2.lookup(ip_address)

        if not match:
            raise IPAddressException("Incorrect ip address")

        weather_provider = OpenWeatherMap(formatter=formatter)

        try:
            conditions = weather_provider.now(lat=match.location[0],
                                              lon=match.location[1],
                                              units=args['units'])
        except WeatherDataException as exc:
            print >> sys.stderr, "Something bad happens({0}), " \
                                 "Please try again later.".format(exc.message)
            sys.exit(1)

        puts(getattr(colored, get_temperature_color(conditions))(conditions))


if __name__ == '__main__':
    Weather.run()
