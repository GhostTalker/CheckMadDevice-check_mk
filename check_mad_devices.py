#!/usr/bin/env python3
__author__ = "GhostTalker"
__copyright__ = "Copyright 2019, The GhostTalker project"
__version__ = "0.1.0"
__status__ = "Dev"

# Generic/Built-in and other Libs
import sys
import requests
import time

# Variables
# check syntax and arguments
if (len(sys.argv) < 5 or len(sys.argv) > 666666):
    print('wrong count of arguments')
    print("check_mad_devices.py <URL> <DEVICE_ORIGIN> <WARN> <CRIT>")
    sys.exit(0)
mad_url = (sys.argv[1])
device_origin = (sys.argv[2])
WARN_TIME = (sys.argv[3])
CRIT_TIME = (sys.argv[4])

# check_mk values
OK_VALUE = 0
WARN_VALUE = 1
CRIT_VALUE = 2
UNKN_VALUE = 3

# funktions
def check_mitm_status_page(url):
    """  Check Response Code and Output from MITM status page """
    global response
    response = requests.get(url)
    if response.status_code == 200:
        return
    elif response.status_code == 404:
        sys.exit(2)
    else:
        sys.exit(2)


def read_device_status_values(device_origin):
    """ Read Values for a device from MITM status page """
    global device_values
    global injection_status
    global latest_data
    global mode_timestamp
    global scan_mode

    # Read Values
    json_respond = response.json()
    devices = (json_respond["origin_status"])
    device_values = (devices[device_origin])
    injection_status = (device_values["injection_status"])
    latest_data = (device_values["latest_data"])
    if latest_data == "None":
        print(" Das Device " + device_origin + " meldet sich nicht beim Server. Reboot via ADB erforderlich")
        exit_value = UNKN_VALUE
        sys.exit(exit_value)
    mode_value = (device_values["mode_value"])
    mode_timestamp = (mode_value["timestamp"])
    mode_values = (mode_value["values"])
    scan_mode = (mode_values["scanmode"])


def check_time_since_last_data():
    """ calculate time between now and latest_data """
    global min_since_last_data
    global latest_data_hr
    actual_time = time.time()
    sec_since_last_data = actual_time - latest_data
    min_since_last_data = sec_since_last_data / 60
    min_since_last_data = int(min_since_last_data)
    latest_data_hr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(latest_data))


def output_check_mk():
    global exit_value
    if int(min_since_last_data) < int(WARN_TIME):
        print(" Das Device " + device_origin + " ist ok! Letztes Lebenszeichen vor " + str(
            min_since_last_data) + " Minute(n). \n Injection-Status : " + str(
            injection_status) + "\n Letzte Verbindung: " + str(latest_data_hr) + "\n Scan-Mode        : " + scan_mode)
        exit_value = OK_VALUE
        return
    elif int(min_since_last_data) < int(CRIT_TIME):
        print(" Das Devoce " + device_origin + " hat sich seit mehr als " + str(
            min_since_last_data) + " Minute(n) nicht mehr gemeldet. Prüfung erforderlich!")
        exit_value = WARN_VALUE
        return
    elif int(min_since_last_data) > int(CRIT_TIME):
        print(" Das Devoce " + device_origin + " hat sich seit mehr als " + str(
            min_since_last_data) + " Minute(n) nicht mehr gemeldet. Reboot via ADB erforderlich")
        exit_value = CRIT_VALUE
        return
    else:
        print(" Das Device " + device_origin + " meldet sich nicht beim Server. Reboot via ADB erforderlich")
        exit_value = UNKN_VALUE
        return


# execute functions with parameters
check_mitm_status_page(mad_url)
read_device_status_values(device_origin)
check_time_since_last_data()
output_check_mk()

# exit
sys.exit(exit_value)
