#!/usr/bin/env python

"""
© Copyright 2015-2016, 3D Robotics.
"""
#
# This is a small example of the python drone API - an ultra minimal GCS
#

import os
import sys
from tkinter import Button, Frame, Label, Tk

from dronekit import VehicleMode, connect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#Set up option parsing to get connection string
import argparse

from _common import add_connection_argument, get_connection_string

parser = argparse.ArgumentParser(description='Tracks GPS position of your computer (Linux only).')
add_connection_argument(parser)
args = parser.parse_args()

connection_string = get_connection_string(args.connect)

# Connect to the Vehicle
print(f'Connecting to vehicle on: {connection_string}')
vehicle = connect(connection_string, wait_ready=True)

def setMode(mode):
    # Now change the vehicle into auto mode
    vehicle.mode = VehicleMode(mode)


def updateGUI(label, value):
    label['text'] = value

def addObserverAndInit(name, cb):
    """We go ahead and call our observer once at startup to get an initial value"""
    vehicle.add_attribute_listener(name, cb)

root = Tk()
root.wm_title("microGCS - the worlds crummiest GCS")
frame = Frame(root)
frame.pack()

locationLabel = Label(frame, text = "No location", width=60)
locationLabel.pack()
attitudeLabel = Label(frame, text = "No Att", width=60)
attitudeLabel.pack()
modeLabel = Label(frame, text = "mode")
modeLabel.pack()

addObserverAndInit('attitude', lambda vehicle, name, attitude: updateGUI(attitudeLabel, vehicle.attitude))
addObserverAndInit('location', lambda vehicle, name, location: updateGUI(locationLabel, str(location.global_frame)))
addObserverAndInit('mode', lambda vehicle,name,mode: updateGUI(modeLabel, mode))

Button(frame, text = "Auto", command = lambda : setMode("AUTO")).pack()
Button(frame, text = "RTL", command = lambda : setMode("RTL")).pack()

root.mainloop()
