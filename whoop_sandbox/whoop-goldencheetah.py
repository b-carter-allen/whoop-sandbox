#!/usr/bin/env python3

import requests  # for getting URL
import json  # for parsing json
from datetime import datetime  # datetime parsing
import pytz  # timezone adjusting
import csv  # for making csv files
import os

#make a secret.py file from secret_template.py, fill in with credentials
from secret import USERNAME
from secret import PASSWORD
from constants import ROOT

#################################################################
# USER VARIABLES

username = USERNAME
password = PASSWORD
save_directory = f"~/{ROOT}/" # keep trailing slash

#################################################################
# GET ACCESS TOKEN

# Post credentials
r = requests.post("https://api-7.whoop.com/oauth/token", json={
    "grant_type": "password",
    "issueRefresh": False,
    "password": password,
    "username": username
})

# Exit if fail
if r.status_code != 200:
    print("Fail - Credentials rejected.")
    exit()
else:
    print("Success - Credentials accepted")

# Set userid/token variables
userid = r.json()['user']['id']
access_token = r.json()['access_token']

#################################################################
# GET DATA

# Download data
url = 'https://api-7.whoop.com/users/{}/cycles'.format(userid)

params = {
    'start': '2000-01-01T00:00:00.000Z',
    'end': '2030-01-01T00:00:00.000Z'
}

headers = {
    'Authorization': 'bearer {}'.format(access_token)
}

r = requests.get(url, params=params, headers=headers)

# Check if user/auth are accepted
if r.status_code != 200:
    print("Fail - User ID / auth token rejected.")
    exit()
else:
    print("Success - User ID / auth token accepted")

#################################################################
# PARSE/TRANSFORM DATA

# Convert data to json
data_raw = r.json()

# Takes a time and offset string and returns a timezone-corrected datetime string


def time_parse(time_string, offset_string):
    # Switch sign on offset
    offset_string = offset_string.replace(
        '-', '+') if offset_string.count('-') else offset_string.replace('+', '-')
    # Remove tz from time and add offset, get to 19 characters
    time_string = time_string[:-(len(time_string) - 19)] + offset_string
    # Parse and format
    oldformat = '%Y-%m-%dT%H:%M:%S%z'
    newformat = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(time_string, oldformat).astimezone(pytz.utc).strftime(newformat)


# Make data object
data_summary = []

# Iterate through data
for d in data_raw:

    # Make record object with default values
    record = {
        'timestamp_measurement': None,
        'HR': None,
        'AVNN': None,
        'SDNN': None,
        'rMSSD': None,
        'pNN50': None,
        'LF': None,
        'HF': None,
        'HRV4T_Recovery_Points': None
    }

    # Recovery
    if (d['recovery'] and
        'timestamp' in d['recovery'] and
        'heartRateVariabilityRmssd' in d['recovery'] and
        isinstance(d['recovery']['heartRateVariabilityRmssd'], (int, float)) and
        d['sleep'] and
        d['sleep']['sleeps'] and
        d['sleep']['sleeps'][0]['timezoneOffset']):

        # This is the timestamp when Whoop processed sleep -
        # not the time of measurement
        record['timestamp_measurement'] = time_parse(
            d['recovery']['timestamp'],
            d['sleep']['sleeps'][0]['timezoneOffset'])
        record['rMSSD'] = d['recovery']['heartRateVariabilityRmssd'] * 1000.0

        if ('restingHeartRate' in d['recovery'] and
            isinstance(d['recovery']['restingHeartRate'], (int, float))):
            record['HR'] = d['recovery']['restingHeartRate']

        # Recovery score
        if ('score' in d['recovery'] and
            isinstance(d['recovery']['score'], (int, float))):
            record['HRV4T_Recovery_Points'] = d['recovery']['score'] / 10.0

        # Append record to data dictionary
        data_summary.append(record)

#################################################################
# WRITE JSON RAW DATA FILE
'''
# Write json file
with open(save_directory + 'whoop_raw.json', 'w') as outfile:
    json.dump(data_raw, outfile)
print("Success - JSON raw data saved.")
'''
#################################################################
# WRITE CSV SUMMARY DATA FILE

# Write to CSV file
with open(os.path.expanduser(save_directory + 'whoop-goldencheetah.csv'), 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=data_summary[0].keys())
    # Write header
    writer.writeheader()
    # Write rows
    for row in data_summary:
        writer.writerow(row)

print("Success - CSV summary data saved.")
