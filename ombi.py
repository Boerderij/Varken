# Do not edit this script. Edit configuration.py
import sys
import requests
from datetime import datetime, timezone
from influxdb import InfluxDBClient
import argparse
from argparse import RawTextHelpFormatter
import configuration

headers = {'Apikey': configuration.ombi_api_key}

def now_iso():
    now_iso = datetime.now(timezone.utc).astimezone().isoformat()
    return now_iso

def influx_sender(influx_payload):
    influx = InfluxDBClient(configuration.influxdb_url, configuration.influxdb_port, configuration.influxdb_username,
                            configuration.influxdb_password, configuration.ombi_influxdb_db_name)
    influx.write_points(influx_payload)

def get_total_requests():
    get_tv_requests = requests.get('{}/api/v1/Request/tv'.format(configuration.ombi_url), headers=headers).json()
    get_movie_requests = requests.get('{}/api/v1/Request/movie'.format(configuration.ombi_url), headers=headers).json()

    count_movie_requests = 0
    count_tv_requests = 0

    for show in get_tv_requests:
        count_tv_requests += 1

    for movie in get_movie_requests:
        count_movie_requests += 1

    influx_payload = [
        {
            "measurement": "Ombi",
            "tags": {
                "type": "Request_Total"
            },
            "time": now_iso(),
            "fields": {
                "total": count_movie_requests + count_tv_requests
            }
        }
    ]
    return influx_payload

def get_request_counts():
    get_request_counts = requests.get('{}/api/v1/Request/count'.format(configuration.ombi_url), headers=headers).json()

    influx_payload = [
        {
        "measurement": "Ombi",
            "tags": {
                "type": "Request_Counts"
            },
            "time": now_iso(),
            "fields": {
                "pending": int(get_request_counts['pending']),
                "approved": int(get_request_counts['approved']),
                "available": int(get_request_counts['available'])
            }
        }
    ]
    return influx_payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Ombi stats operations',
        description='Script to aid in data gathering from Ombi', formatter_class=RawTextHelpFormatter)

    parser.add_argument("--total",  action='store_true',
        help='Get the total count of all requests')

    parser.add_argument("--counts",  action='store_true',
        help='Get the count of pending, approved, and available requests')

    opts = parser.parse_args()

    if opts.total:
        influx_sender(get_total_requests())

    elif opts.counts:
        influx_sender(get_request_counts())

    elif len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
