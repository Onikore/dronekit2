#!/usr/bin/env python

"""
© Copyright 2015-2016, 3D Robotics.
performance_test.py:

This performance test logs the interval between messages being
sent by Dronekit-Python and an acknowledgment being received
from the autopilot. It provides a running report of the maximum,
minimum, and most recent interval for 30 seconds.

Full documentation is provided at http://python.dronekit.io/examples/performance_test.html
"""
import os
import sys
import time
from datetime import datetime

from pymavlink import mavutil

from dronekit import connect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#Set up option parsing to get connection string
import argparse

from _common import add_connection_argument, get_connection_string

parser = argparse.ArgumentParser(description='Generates max, min and current interval between message sent and ack recieved.')
add_connection_argument(parser)
args = parser.parse_args()

connection_string = get_connection_string(args.connect)


# Connect to the Vehicle
print(f'Connecting to vehicle on: {connection_string}')
vehicle = connect(connection_string, wait_ready=True)

#global vehicle


def cur_usec():
    """Return current time in usecs"""
    # t = time.time()
    dt = datetime.now()
    t = dt.minute * 60 + dt.second + dt.microsecond / (1e6)
    return t

class MeasureTime:
    def __init__(self):
        self.prevtime = cur_usec()
        self.previnterval = 0
        self.numcount = 0
        self.reset()

    def reset(self):
        self.maxinterval = 0
        self.mininterval = 10000

    def log(self):
        #print "Interval", self.previnterval
        #print "MaxInterval", self.maxinterval
        #print "MinInterval", self.mininterval
        sys.stdout.write(f'MaxInterval: {self.maxinterval}\tMinInterval: {self.mininterval}\tInterval: {self.previnterval}\r')
        sys.stdout.flush()


    def update(self):
        now = cur_usec()
        self.numcount = self.numcount + 1
        self.previnterval = now - self.prevtime
        self.prevtime = now
        if self.numcount>1: #ignore first value where self.prevtime not reliable.
            self.maxinterval = max(self.previnterval, self.maxinterval)
            self.mininterval = min(self.mininterval, self.previnterval)
            self.log()


acktime = MeasureTime()


#Create COMMAND_ACK message listener.
@vehicle.on_message('COMMAND_ACK')
def listener(self, name, message):
    acktime.update()
    send_testpackets()


def send_testpackets():
    #Send message using `command_long_encode` (returns an ACK)
    msg = vehicle.message_factory.command_long_encode(
                                                    1, 1,    # target system, target component
                                                    #mavutil.mavlink.MAV_CMD_DO_SET_RELAY, #command
                                                    mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
                                                    0, #confirmation
                                                    0, 0, 0, 0, #params 1-4
                                                    0,
                                                    0,
                                                    0
                                                    )

    vehicle.send_mavlink(msg)

#Start logging by sending a test packet
send_testpackets()

print("Logging for 30 seconds")
for _ in range(1,30):
    time.sleep(1)

# Close vehicle object before exiting script
vehicle.close()
