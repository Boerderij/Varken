#!/usr/bin/env python3
# To use:
# docker exec -it varken cp /app/data/utilities/grafana_build.py /config/grafana_build.py
# nano /opt/dockerconfigs/varken/grafana_build.py   # Edit vars. This assumes you have your persistent data there
# docker exec -it varken python3 /config/grafana_build.py
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
music_library = 'Music'
usg_name = 'Gateway'
ombi_url = 'https://yourdomain.com/ombi'
tautulli_url = 'https://yourdomain.com/tautulli'
sonarr_url = 'https://yourdomain.com/sonarr'
radarr_url = 'https://yourdomain.com/radarr'
sickchill_url = 'https://yourdomain.com/sickchill'
lidarr_url = 'https://yourdomain.com/lidarr'

# Do not edit past this line #
session = Session()
auth = (username, password)
url_base = f"{grafana_url.rstrip('/')}/api"

varken_datasource = []
datasource_name = "Varken-Script"
try:
    datasources = session.get(url_base + '/datasources', auth=auth, verify=verify).json()
    varken_datasource = [source for source in datasources if source['database'] == 'varken']
    if varken_datasource:
        print(f'varken datasource already exists with the name "{varken_datasource[0]["name"]}"')
        datasource_name = varken_datasource[0]["name"]
except JSONDecodeError:
    exit(f"Could not talk to grafana at {grafana_url}. Check URL/Username/Password")

if not varken_datasource:
    datasource_data = {
        "name": datasource_name,
        "type": "influxdb",
        "url": f"http://{'influxdb' if docker else host_ip}:8086",
        "access": "proxy",
        "basicAuth": False,
        "database": 'varken'
    }
    post = session.post(url_base + '/datasources', auth=auth, verify=verify, json=datasource_data).json()
    print(f'Created {datasource_name} datasource (id:{post["datasource"]["id"]})')

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
            "value": datasource_name
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
            "name": "VAR_MUSICLIBRARY",
            "type": "constant",
            "label": "Music Library Name",
            "value": music_library,
            "description": ""
        },
        {
            "name": "VAR_USGNAME",
            "type": "constant",
            "label": "Unifi USG Name",
            "value": usg_name,
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
        },
        {
          "name": "VAR_LIDARRURL",
          "type": "constant",
          "label": "lidarr URL",
          "value": lidarr_url,
          "description": ""
        }
    ]
}
try:
    make_dashboard = session.post(url_base + '/dashboards/import', json=dashboard_data, auth=auth, verify=verify)
    if make_dashboard.status_code == 200 and make_dashboard.json().get('imported'):
        print(f'Created dashboard "{our_dashboard["title"]}"')
except:
    print('Shit...')
