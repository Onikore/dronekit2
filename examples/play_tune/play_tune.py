#!/usr/bin/env python

"""
© Copyright 2017, Peter Barker
play_tune.py: GUIDED mode "simple goto" example (Copter Only)

Demonstrates how to play a custom tune on a vehicle using the vehicle's buzzer

Full documentation is provided at http://python.dronekit.io/examples/play_tune.html
"""

import os
import sys

from dronekit import connect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Set up option parsing to get connection string
import argparse

from _common import add_connection_argument, get_connection_string

parser = argparse.ArgumentParser(description='Play tune on vehicle buzzer.')
add_connection_argument(parser)
parser.add_argument('--tune', type=str, help="tune to play", default="AAAA")
args = parser.parse_args()

connection_string = get_connection_string(args.connect)


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

vehicle.play_tune(args.tune)
