#!/usr/bin/env python

"""
© Copyright 2015-2016, 3D Robotics.

channel_overrides.py:

Demonstrates how set and clear channel-override information.

# NOTE:
Channel overrides (a.k.a "RC overrides") are highly discommended (they are primarily implemented
for simulating user input and when implementing certain types of joystick control).

They are provided for development purposes. Please raise an issue explaining why you need them
and we will try to find a better alternative: https://github.com/dronekit/dronekit-python/issues

Full documentation is provided at http://python.dronekit.io/examples/channel_overrides.html
"""
import os
import sys

from dronekit import connect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#Set up option parsing to get connection string
import argparse

from _common import add_connection_argument, get_connection_string

parser = argparse.ArgumentParser(
    description='Example showing how to set and clear vehicle channel-override information.')
add_connection_argument(parser)
args = parser.parse_args()

connection_string = get_connection_string(args.connect)


# Connect to the Vehicle
print(f'Connecting to vehicle on: {connection_string}')
vehicle = connect(connection_string, wait_ready=True)

# Get all original channel values (before override)
print("Channel values from RC Tx:", vehicle.channels)

# Access channels individually
print("Read channels individually:")
print(f" Ch1: {vehicle.channels['1']}")
print(f" Ch2: {vehicle.channels['2']}")
print(f" Ch3: {vehicle.channels['3']}")
print(f" Ch4: {vehicle.channels['4']}")
print(f" Ch5: {vehicle.channels['5']}")
print(f" Ch6: {vehicle.channels['6']}")
print(f" Ch7: {vehicle.channels['7']}")
print(f" Ch8: {vehicle.channels['8']}")
print(f"Number of channels: {len(vehicle.channels)}")


# Override channels
print(f"\nChannel overrides: {vehicle.channels.overrides}")

print("Set Ch2 override to 200 (indexing syntax)")
vehicle.channels.overrides['2'] = 200
print(f" Channel overrides: {vehicle.channels.overrides}")
print(f" Ch2 override: {vehicle.channels.overrides['2']}")

print("Set Ch3 override to 300 (dictionary syntax)")
vehicle.channels.overrides = {'3':300}
print(f" Channel overrides: {vehicle.channels.overrides}")

print("Set Ch1-Ch8 overrides to 110-810 respectively")
vehicle.channels.overrides = {'1': 110, '2': 210,'3': 310,'4':4100, '5':510,'6':610,'7':710,'8':810}
print(f" Channel overrides: {vehicle.channels.overrides}")


# Clear override by setting channels to None
print("\nCancel Ch2 override (indexing syntax)")
vehicle.channels.overrides['2'] = None
print(f" Channel overrides: {vehicle.channels.overrides}")

print("Clear Ch3 override (del syntax)")
del vehicle.channels.overrides['3']
print(f" Channel overrides: {vehicle.channels.overrides}")

print("Clear Ch5, Ch6 override and set channel 3 to 500 (dictionary syntax)")
vehicle.channels.overrides = {'5':None, '6':None,'3':500}
print(f" Channel overrides: {vehicle.channels.overrides}")

print("Clear all overrides")
vehicle.channels.overrides = {}
print(f" Channel overrides: {vehicle.channels.overrides}")

#Close vehicle object before exiting script
print("\nClose vehicle object")
vehicle.close()

print("Completed")
