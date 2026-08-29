#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dronekit import connect
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from _common import add_connection_argument, get_connection_string

# Set up option parsing to get connection string
import argparse
parser = argparse.ArgumentParser(description='Reboots vehicle')
add_connection_argument(parser)
args = parser.parse_args()

connection_string = get_connection_string(args.connect)


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

vehicle.reboot()
time.sleep(1)
