#!/usr/bin/env python

"""
© Copyright 2015-2016, 3D Robotics.

create_attribute.py:

Demonstrates how to create attributes from MAVLink messages within your DroneKit-Python script
and use them in the same way as the built-in Vehicle attributes.

The code adds a new attribute to the Vehicle class, populating it with information from RAW_IMU messages
intercepted using the message_listener decorator.

Full documentation is provided at http://python.dronekit.io/examples/create_attribute.html
"""

import os
import sys
import time

from my_vehicle import MyVehicle  #Our custom vehicle class

from dronekit import connect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#Set up option parsing to get connection string
import argparse

from _common import add_connection_argument, get_connection_string

parser = argparse.ArgumentParser(description='Demonstrates how to create attributes from MAVLink messages. ')
add_connection_argument(parser)
args = parser.parse_args()

connection_string = get_connection_string(args.connect)


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True, vehicle_class=MyVehicle)

# Add observer for the custom attribute

def raw_imu_callback(self, attr_name, value):
    # attr_name == 'raw_imu'
    # value == vehicle.raw_imu
    print(value)

vehicle.add_attribute_listener('raw_imu', raw_imu_callback)

print('Display RAW_IMU messages for 5 seconds and then exit.')
time.sleep(5)

#The message listener can be unset using ``vehicle.remove_message_listener``

#Close vehicle object before exiting script
print("Close vehicle object")
vehicle.close()
