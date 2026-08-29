#!/usr/bin/env python

"""
© Copyright 2015-2016, 3D Robotics.
vehicle_state.py:

Demonstrates how to get and set vehicle state and parameter information,
and how to observe vehicle attribute (state) changes.

Full documentation is provided at http://python.dronekit.io/examples/vehicle_state.html
"""
import os
import sys
import time

from dronekit import VehicleMode, connect

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#Set up option parsing to get connection string
import argparse

from _common import add_connection_argument, get_connection_string

parser = argparse.ArgumentParser(description='Print out vehicle state information.')
add_connection_argument(parser)
args = parser.parse_args()

connection_string = get_connection_string(args.connect)


# Connect to the Vehicle.
#   Set `wait_ready=True` to ensure default attributes are populated before `connect()` returns.
print(f"\nConnecting to vehicle on: {connection_string}")
vehicle = connect(connection_string, wait_ready=True)

vehicle.wait_ready('autopilot_version')

# Get all vehicle attributes (state)
print("\nGet all vehicle attribute values:")
print(f" Autopilot Firmware version: {vehicle.version}")
print(f"   Major version number: {vehicle.version.major}")
print(f"   Minor version number: {vehicle.version.minor}")
print(f"   Patch version number: {vehicle.version.patch}")
print(f"   Release type: {vehicle.version.release_type()}")
print(f"   Release version: {vehicle.version.release_version()}")
print(f"   Stable release?: {vehicle.version.is_stable()}")
print(" Autopilot capabilities")
print(f"   Supports MISSION_FLOAT message type: {vehicle.capabilities.mission_float}")
print(f"   Supports PARAM_FLOAT message type: {vehicle.capabilities.param_float}")
print(f"   Supports MISSION_INT message type: {vehicle.capabilities.mission_int}")
print(f"   Supports COMMAND_INT message type: {vehicle.capabilities.command_int}")
print(f"   Supports PARAM_UNION message type: {vehicle.capabilities.param_union}")
print(f"   Supports ftp for file transfers: {vehicle.capabilities.ftp}")
print(f"   Supports commanding attitude offboard: {vehicle.capabilities.set_attitude_target}")
print(f"   Supports commanding position and velocity targets in local NED frame: {vehicle.capabilities.set_attitude_target_local_ned}")
print(f"   Supports set position + velocity targets in global scaled integers: {vehicle.capabilities.set_altitude_target_global_int}")
print(f"   Supports terrain protocol / data handling: {vehicle.capabilities.terrain}")
print(f"   Supports direct actuator control: {vehicle.capabilities.set_actuator_target}")
print(f"   Supports the flight termination command: {vehicle.capabilities.flight_termination}")
print(f"   Supports mission_float message type: {vehicle.capabilities.mission_float}")
print(f"   Supports onboard compass calibration: {vehicle.capabilities.compass_calibration}")
print(f" Global Location: {vehicle.location.global_frame}")
print(f" Global Location (relative altitude): {vehicle.location.global_relative_frame}")
print(f" Local Location: {vehicle.location.local_frame}")
print(f" Attitude: {vehicle.attitude}")
print(f" Velocity: {vehicle.velocity}")
print(f" GPS: {vehicle.gps_0}")
print(f" Gimbal status: {vehicle.gimbal}")
print(f" Battery: {vehicle.battery}")
print(f" EKF OK?: {vehicle.ekf_ok}")
print(f" Last Heartbeat: {vehicle.last_heartbeat}")
print(f" Rangefinder: {vehicle.rangefinder}")
print(f" Rangefinder distance: {vehicle.rangefinder.distance}")
print(f" Rangefinder voltage: {vehicle.rangefinder.voltage}")
print(f" Heading: {vehicle.heading}")
print(f" Is Armable?: {vehicle.is_armable}")
print(f" System status: {vehicle.system_status.state}")
print(f" Groundspeed: {vehicle.groundspeed}")    # settable
print(f" Airspeed: {vehicle.airspeed}")    # settable
print(f" Mode: {vehicle.mode.name}")    # settable
print(f" Armed: {vehicle.armed}")    # settable



# Get Vehicle Home location - will be `None` until first set by autopilot
while not vehicle.home_location:
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    if not vehicle.home_location:
        print(" Waiting for home location ...")
# We have a home location, so print it!
print(f"\n Home location: {vehicle.home_location}")


# Set vehicle home_location, mode, and armed attributes (the only settable attributes)

print("\nSet new home location")
# Home location must be within 50km of EKF home location (or setting will fail silently)
# In this case, just set value to current location with an easily recognisable altitude (222)
my_location_alt = vehicle.location.global_frame
my_location_alt.alt = 222.0
vehicle.home_location = my_location_alt
print(f" New Home Location (from attribute - altitude should be 222): {vehicle.home_location}")

#Confirm current value on vehicle by re-downloading commands
cmds = vehicle.commands
cmds.download()
cmds.wait_ready()
print(f" New Home Location (from vehicle - altitude should be 222): {vehicle.home_location}")


print(f"\nSet Vehicle.mode = GUIDED (currently: {vehicle.mode.name})")
vehicle.mode = VehicleMode("GUIDED")
while not vehicle.mode.name=='GUIDED':  #Wait until mode has changed
    print(" Waiting for mode change ...")
    time.sleep(1)


# Check that vehicle is armable
while not vehicle.is_armable:
    print(" Waiting for vehicle to initialise...")
    time.sleep(1)
    # If required, you can provide additional information about initialisation
    # using `vehicle.gps_0.fix_type` and `vehicle.mode.name`.

#print "\nSet Vehicle.armed=True (currently: %s)" % vehicle.armed
#vehicle.armed = True
#while not vehicle.armed:
#    print " Waiting for arming..."
#    time.sleep(1)
#print " Vehicle is armed: %s" % vehicle.armed


# Add and remove and attribute callbacks

#Define callback for `vehicle.attitude` observer
last_attitude_cache = None
def attitude_callback(self, attr_name, value):
    # `attr_name` - the observed attribute (used if callback is used for multiple attributes)
    # `self` - the associated vehicle object (used if a callback is different for multiple vehicles)
    # `value` is the updated attribute value.
    global last_attitude_cache
    # Only publish when value changes
    if value!=last_attitude_cache:
        print(" CALLBACK: Attitude changed to", value)
        last_attitude_cache=value

print("\nAdd `attitude` attribute callback/observer on `vehicle`")
vehicle.add_attribute_listener('attitude', attitude_callback)

print(" Wait 2s so callback invoked before observer removed")
time.sleep(2)

print(" Remove Vehicle.attitude observer")
# Remove observer added with `add_attribute_listener()` specifying the attribute and callback function
vehicle.remove_attribute_listener('attitude', attitude_callback)



# Add mode attribute callback using decorator (callbacks added this way cannot be removed).
print("\nAdd `mode` attribute callback/observer using decorator")
@vehicle.on_attribute('mode')
def decorated_mode_callback(self, attr_name, value):
    # `attr_name` is the observed attribute (used if callback is used for multiple attributes)
    # `attr_name` - the observed attribute (used if callback is used for multiple attributes)
    # `value` is the updated attribute value.
    print(" CALLBACK: Mode changed to", value)

print(f" Set mode=STABILIZE (currently: {vehicle.mode.name}) and wait for callback")
vehicle.mode = VehicleMode("STABILIZE")

print(" Wait 2s so callback invoked before moving to next example")
time.sleep(2)

print("\n Attempt to remove observer added with `on_attribute` decorator (should fail)")
try:
    vehicle.remove_attribute_listener('mode', decorated_mode_callback)
except:
    print(" Exception: Cannot remove observer added using decorator")




# Demonstrate getting callback on any attribute change
def wildcard_callback(self, attr_name, value):
    print(f" CALLBACK: ({attr_name}): {value}")

print("\nAdd attribute callback detecting ANY attribute change")
vehicle.add_attribute_listener('*', wildcard_callback)


print(" Wait 1s so callback invoked before observer removed")
time.sleep(1)

print(" Remove Vehicle attribute observer")
# Remove observer added with `add_attribute_listener()`
vehicle.remove_attribute_listener('*', wildcard_callback)



# Get/Set Vehicle Parameters
print("\nRead and write parameters")
print(f" Read vehicle param 'THR_MIN': {vehicle.parameters['THR_MIN']}")

print(" Write vehicle param 'THR_MIN' : 10")
vehicle.parameters['THR_MIN']=10
print(f" Read new value of param 'THR_MIN': {vehicle.parameters['THR_MIN']}")


print("\nPrint all parameters (iterate `vehicle.parameters`):")
for key, value in vehicle.parameters.items():
    print(f" Key:{key} Value:{value}")


print("\nCreate parameter observer using decorator")
# Parameter string is case-insensitive
# Value is cached (listeners are only updated on change)
# Observer added using decorator can't be removed.

@vehicle.parameters.on_attribute('THR_MIN')
def decorated_thr_min_callback(self, attr_name, value):
    print(f" PARAMETER CALLBACK: {attr_name} changed to: {value}")


print("Write vehicle param 'THR_MIN' : 20 (and wait for callback)")
vehicle.parameters['THR_MIN']=20
for x in range(1,5):
    #Callbacks may not be updated for a few seconds
    if vehicle.parameters['THR_MIN']==20:
        break
    time.sleep(1)


#Callback function for "any" parameter
print("\nCreate (removable) observer for any parameter using wildcard string")
def any_parameter_callback(self, attr_name, value):
    print(f" ANY PARAMETER CALLBACK: {attr_name} changed to: {value}")

#Add observer for the vehicle's any/all parameters parameter (defined using wildcard string ``'*'``)
vehicle.parameters.add_attribute_listener('*', any_parameter_callback)
print(" Change THR_MID and THR_MIN parameters (and wait for callback)")
vehicle.parameters['THR_MID']=400
vehicle.parameters['THR_MIN']=30


## Reset variables to sensible values.
print("\nReset vehicle attributes/parameters and exit")
vehicle.mode = VehicleMode("STABILIZE")
#vehicle.armed = False
vehicle.parameters['THR_MIN']=130
vehicle.parameters['THR_MID']=500


#Close vehicle object before exiting script
print("\nClose vehicle object")
vehicle.close()

print("Completed")




