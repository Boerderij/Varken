# Varken
Dutch for PIG. PIG is an Acronym for Plex/InfluxDB/Grafana

Varken is a standalone command-line utility to aggregate data
from the plex ecosystem into InfluxDB. Examples use Grafana for a
frontend

Requirements /w install links: [Grafana](http://docs.grafana.org/installation/), [Python3](https://www.python.org/downloads/), [InfluxDB](https://docs.influxdata.com/influxdb/v1.5/introduction/installation/)

<p align="center">
<img width="800" src="https://i.imgur.com/av8e0HP.png">
</p>

## Quick Setup (Varken Alpha)
1. Clone the repository `sudo git clone https://github.com/DirtyCajunRice/grafana-scripts.git /opt/Varken`
1. Follow the systemd install instructions located in `varken.systemd`
1. Create venv in project `/usr/bin/python3 -m venv varken-venv`
1. Install requirements `/opt/Varken/varken-venv/bin/python -m pip install -r requirements.txt`
1. Make a copy of `varken.example.ini` to `varken.ini` in the `data` folder
   `cp /opt/Varken/data/varken.example.ini /opt/Varken/data/varken.ini`
1. Make the appropriate changes to `varken.ini`
   ie.`nano /opt/Varken/data/varken.ini`
1. After completing the [getting started](http://docs.grafana.org/guides/getting_started/) portion of grafana, create your datasource for influxdb.
1. Install `grafana-cli plugins install grafana-worldmap-panel`
1. TODO:: Click the + on your menu and click import. Using the .json provided in this repo, paste it in and customize as you like.

### Docker

Repo is included in [si0972/grafana-scripts-docker](https://github.com/si0972/grafana-scripts-docker/tree/varken)

<details><summary>Example</summary>
<p>

```
docker create \
  --name=grafana-scripts \
  -v <path to data>:/Scripts \
  -e PGID=<gid> -e PUID=<uid>  \
  si0972/grafana-scripts:varken
```
</p>
</details>
