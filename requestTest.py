"""
Adapted from: https://gist.github.com/arnesund/29ffa1cdabacabe323d3bc45bc7db3fb
Designed to be run every 8-10 minutes with crontab on a raspberry pi

Pulls users Netatmo weather station data and writes it to a Influxdb database
"""
#!/usr/bin/env python
import os
import sys
import json
import time
import requests
import configparser

# Parse the config file
config = configparser.ConfigParser()
config.read('config.ini')

# Make sure you put the corrent data in the config.ini file
# Pull user specific influxdb data from config.ini
INFLUX_HOST = config['INFLUX']['HOST']
INFLUX_PORT = config['INFLUX']['PORT']
INFLUX_DATABASE = config['INFLUX']['DATABASE']
INFLUX_USER = config['INFLUX']['USER']
INFLUX_PASS = config['INFLUX']['PASSWORD']

# Pull user specific netatmo data from config.ini
NETATMO_CLIENT_ID = config['NETATMO']['CLIENT_ID']
NETATMO_CLIENT_SECRET = config['NETATMO']['CLIENT_SECRET']
NETATMO_USERNAME = config['NETATMO']['USERNAME']
NETATMO_PASSWORD = config['NETATMO']['PASSWORD']

INFLUXDB_WRITE_URL = f"http://{INFLUX_HOST}:{INFLUX_PORT}/write?precision=s&db={INFLUX_DATABASE}&u={INFLUX_USER}&p={INFLUX_PASS}"

# Debug output to verify Influxdb endpoint
# print(f"Will write measurements to InfluxDB at endpoint {INFLUXDB_WRITE_URL}")

# Data structure for Netatmo request
data = dict(grant_type='password', client_id=NETATMO_CLIENT_ID,
       client_secret=NETATMO_CLIENT_SECRET, username=NETATMO_USERNAME,
       password=NETATMO_PASSWORD, scope='read_station')

resp = requests.post('https://api.netatmo.com/oauth2/token', data=data)
if resp.status_code == 200:
    token = resp.json()
    token['expiry'] = int(time.time()) + token['expires_in']

# Check if token needs refresh
if token['expiry'] - int(time.time()) < 600:
    data = dict(grant_type='refresh_token', refresh_token=token['refresh_token'], client_id=NETATMO_CLIENT_ID, client_secret=NETATMO_CLIENT_SECRET)
    resp = requests.post('https://api.netatmo.com/oauth2/token', data=data)
    if resp.status_code == 200:
        token = resp.json()
        token['expiry'] = int(time.time()) + token['expires_in']

# Debug output current time for logs
print(time.strftime("%Y:%m:%d-%H:%M:%S"))
# Fetch measurements
resp = requests.get('https://api.netatmo.com/api/getstationsdata?access_token=' + token['access_token'])
if resp.status_code == 200:
    data = resp.json()
    payload = ""
    for device in data['body']['devices']:
        timeStamp = device['dashboard_data']['time_utc']
        # Normalize station name and module names to ensure they become valid InfluxDB label values
        stationName = device['station_name'].replace(' ', '_')
        moduleName = device['module_name'].replace(' ', '_')
        for datatype in device['data_type']:
            payload += f"{datatype},station_name={stationName},module_name={moduleName} value={device['dashboard_data'][datatype]} {timeStamp}\n"
        for module in device['modules']:
            moduleName = module['module_name'].replace(' ', '_')
            for datatype in module['data_type']:
                payload += f"{datatype},station_name={stationName},module_name={moduleName} value={module['dashboard_data'][datatype]} {timeStamp}\n"
            payload += f"battery_percent,station_name={stationName},module_name={moduleName} value={module['battery_percent']} {timeStamp}\n"

    # Debug output to ensure payload contains data and has valid InfluxDB format
    print('Writing the following data points to InfluxDB:')
    print(payload)

    # Write to InfluxDB
    resp = requests.post(INFLUXDB_WRITE_URL, data=payload)
