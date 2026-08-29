#!/usr/bin/env python

"""
© Copyright 2015-2016, 3D Robotics.
drone_delivery.py:

A Flask based web application that displays a mapbox map to let you view the current vehicle position and
send the vehicle commands to fly to a particular latitude and longitude.
"""

import json
import os
import sys
import time

from flask import Flask, jsonify, request
from jinja2 import Environment, FileSystemLoader

from dronekit import LocationGlobal, LocationGlobalRelative, VehicleMode, connect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Set up option parsing to get connection string
import argparse

from _common import add_connection_argument, get_connection_string

parser = argparse.ArgumentParser(
    description='Creates a Flask based web application that displays a mapbox map to let you view the '
                'current vehicle position and send the vehicle commands to fly to a particular latitude '
                'and longitude.')
add_connection_argument(parser)
parser.add_argument('--mapbox-token',
                    help="Mapbox access token used to render the map. Overrides the MAPBOX_ACCESS_TOKEN "
                         "environment variable.")
args = parser.parse_args()

connection_string = get_connection_string(args.connect)

mapbox_token = args.mapbox_token or os.environ.get('MAPBOX_ACCESS_TOKEN')
if not mapbox_token:
    raise SystemExit(
        "No Mapbox access token provided. Get a free token from https://www.mapbox.com/ "
        "and either set the MAPBOX_ACCESS_TOKEN environment variable or pass --mapbox-token."
    )

local_path = os.path.dirname(os.path.abspath(__file__))
print(f"local path: {local_path}")


class Drone:
    def __init__(self, server_enabled=True):
        self.gps_lock = False
        self.altitude = 30.0

        # Connect to the Vehicle
        self._log('Connected to vehicle.')
        self.vehicle = vehicle
        self.commands = self.vehicle.commands
        self.current_coords = []
        self.webserver_enabled = server_enabled
        self._log("DroneDelivery Start")

        # Register observers
        self.vehicle.add_attribute_listener('location', self.location_callback)

    def launch(self):
        self._log("Waiting for location...")
        while self.vehicle.location.global_frame.lat == 0:
            time.sleep(0.1)
        self.home_coords = [self.vehicle.location.global_frame.lat,
                            self.vehicle.location.global_frame.lon]

        self._log("Waiting for ability to arm...")
        while not self.vehicle.is_armable:
            time.sleep(.1)

        self._log('Running initial boot sequence')
        self.change_mode('GUIDED')
        self.arm()
        self.takeoff()

        if self.webserver_enabled is True:
            self._run_server()

    def takeoff(self):
        self._log("Taking off")
        self.vehicle.simple_takeoff(30.0)

    def arm(self, value=True):
        if value:
            self._log('Waiting for arming...')
            self.vehicle.armed = True
            while not self.vehicle.armed:
                time.sleep(.1)
        else:
            self._log("Disarming!")
            self.vehicle.armed = False

    def _run_server(self):
        # Start web server if enabled
        templates = Templates(self.home_coords)

        app = Flask(
            __name__,
            static_folder=os.path.join(local_path, 'html', 'assets'),
            static_url_path='/static',
        )

        @app.route('/')
        def index():
            return templates.index()

        @app.route('/command')
        def command():
            return templates.command(self.get_location())

        @app.route('/vehicle')
        def vehicle_position():
            return jsonify(position=self.get_location())

        @app.route('/track', methods=['GET', 'POST'])
        def track():
            if request.method == 'POST':
                lat = request.form.get('lat')
                lon = request.form.get('lon')
                if lat is not None and lon is not None:
                    self.goto([lat, lon], True)
            return templates.track(self.get_location())

        print('''Server is bound on all addresses, port 8080
You may connect to it using your web broser using a URL looking like this:
http://localhost:8080/
''')
        app.run(host='0.0.0.0', port=8080)

    def change_mode(self, mode):
        self._log(f"Changing to mode: {mode}")

        self.vehicle.mode = VehicleMode(mode)
        while self.vehicle.mode.name != mode:
            self._log(f'  ... polled mode: {mode}')
            time.sleep(1)

    def goto(self, location, relative=None):
        self._log(f"Goto: {location}, {self.altitude}")

        if relative:
            self.vehicle.simple_goto(
                LocationGlobalRelative(
                    float(location[0]), float(location[1]),
                    float(self.altitude)
                )
            )
        else:
            self.vehicle.simple_goto(
                LocationGlobal(
                    float(location[0]), float(location[1]),
                    float(self.altitude)
                )
            )
        self.vehicle.flush()

    def get_location(self):
        return [self.current_location.lat, self.current_location.lon]

    def location_callback(self, vehicle, name, location):
        if location.global_relative_frame.alt is not None:
            self.altitude = location.global_relative_frame.alt

        self.current_location = location.global_relative_frame

    def _log(self, message):
        print(f"[DEBUG]: {message}")


class Templates:
    def __init__(self, home_coords):
        self.home_coords = home_coords
        self.options = self.get_options()
        self.environment = Environment(loader=FileSystemLoader(local_path + '/html'))

    def get_options(self):
        return {'width': 670,
                'height': 470,
                'zoom': 13,
                'format': 'png',
                'access_token': mapbox_token,
                'mapid': 'kevin3dr.n56ffjoo',
                'home_coords': self.home_coords,
                'menu': [{'name': 'Home', 'location': '/'},
                         {'name': 'Track', 'location': '/track'},
                         {'name': 'Command', 'location': '/command'}],
                'current_url': '/',
                'json': ''
                }

    def index(self):
        self.options = self.get_options()
        self.options['current_url'] = '/'
        return self.get_template('index')

    def track(self, current_coords):
        self.options = self.get_options()
        self.options['current_url'] = '/track'
        self.options['current_coords'] = current_coords
        self.options['json'] = json.dumps(self.options)
        return self.get_template('track')

    def command(self, current_coords):
        self.options = self.get_options()
        self.options['current_url'] = '/command'
        self.options['current_coords'] = current_coords
        return self.get_template('command')

    def get_template(self, file_name):
        template = self.environment.get_template(file_name + '.html')
        return template.render(options=self.options)


# Connect to the Vehicle
print(f'Connecting to vehicle on: {connection_string}')
vehicle = connect(connection_string, wait_ready=True)

print('Launching Drone...')
Drone().launch()
