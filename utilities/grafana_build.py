#!/usr/bin/env python3
from sys import exit
from requests import Session
from json.decoder import JSONDecodeError

docker = True  # True if using a docker container, False if not
host_ip = '127.0.0.1'  # Only relevant if docker = False
username = 'admin'  # Grafana username
password = 'admin'  # Grafana password
grafana_url = 'http://grafana:3000'
verify = False  # Verify SSL

# Do not remove any of these, just change the ones you use
movies_library = 'Movies'
fourk_movies_library = 'Movies 4K'
tv_shows_library = 'TV Shows'
fourk_tv_shows_library = 'TV Shows 4K'
ombi_url = 'https://yourdomain.com/ombi'
tautulli_url = 'https://yourdomain.com/tautulli'
sonarr_url = 'https://yourdomain.com/sonarr'
radarr_url = 'https://yourdomain.com/radarr'
sickchill_url = 'https://yourdomain.com/sickchill'


# Do not edit past this line #
session = Session()
auth = (username, password)
url_base = f"{grafana_url.rstrip('/')}/api"

try:
    datasources = session.get(url_base + '/datasources', auth=auth, verify=verify).json()
    varken_datasource = [source for source in datasources if source['database'] == 'varken']
    if varken_datasource:
        exit(f'varken datasource already exists with the name "{varken_datasource[0]["name"]}"')
except JSONDecodeError:
    exit(f"Could not talk to grafana at {grafana_url}. Check URL/Username/Password")

datasource_data = {
    "name": "Varken-Script",
    "type": "influxdb",
    "url": f"http://{'influxdb' if docker else host_ip}:8086",
    "access": "proxy",
    "basicAuth": False,
    "database": 'varken'
}
post = session.post(url_base + '/datasources', auth=auth, verify=verify, json=datasource_data).json()
print(f'Created Varken-Script datasource (id:{post["datasource"]["id"]})')

our_dashboard = session.get(url_base + '/gnet/dashboards/9585', auth=auth, verify=verify).json()['json']
dashboard_data = {
    "dashboard": our_dashboard,
    "overwrite": True,
    "inputs": [
        {
            "name": "DS_VARKEN",
            "label": "varken",
            "description": "",
            "type": "datasource",
            "pluginId": "influxdb",
            "pluginName": "InfluxDB",
            "value": "Varken-Script"
        },
        {
            "name": "VAR_MOVIESLIBRARY",
            "type": "constant",
            "label": "Movies Library Name",
            "value": movies_library,
            "description": ""
        },
        {
            "name": "VAR_MOVIES4KLIBRARY",
            "type": "constant",
            "label": "4K Movies Library Name",
            "value": fourk_movies_library,
            "description": ""
        },
        {
            "name": "VAR_TVLIBRARY",
            "type": "constant",
            "label": "TV Library Name",
            "value": tv_shows_library,
            "description": ""
        },
        {
            "name": "VAR_TV4KLIBRARY",
            "type": "constant",
            "label": "TV 4K Library Name",
            "value": fourk_tv_shows_library,
            "description": ""
        },
        {
            "name": "VAR_OMBIURL",
            "type": "constant",
            "label": "Ombi URL",
            "value": ombi_url,
            "description": ""
        },
        {
            "name": "VAR_TAUTULLIURL",
            "type": "constant",
            "label": "Tautulli URL",
            "value": tautulli_url,
            "description": ""
        },
        {
            "name": "VAR_SONARRURL",
            "type": "constant",
            "label": "Sonarr URL",
            "value": sonarr_url,
            "description": ""
        },
        {
            "name": "VAR_RADARRURL",
            "type": "constant",
            "label": "Radarr URL",
            "value": radarr_url,
            "description": ""
        },
        {
            "name": "VAR_SICKCHILLURL",
            "type": "constant",
            "label": "Sickchill URL",
            "value": sickchill_url,
            "description": ""
        }
    ]
}
make_dashboard = session.post(url_base + '/dashboards/import', data=dashboard_data, auth=auth, verify=verify)
print('Created dashboard "Varken-Script"')
