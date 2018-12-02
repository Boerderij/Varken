# Varken
Dutch for PIG. PIG is an Acronym for Plex/InfluxDB/Grafana

Varken is a standalone commmand-line utility that will aggregate date
from the plex ecosystem into influxdb to be displayed in grafana

Requirements /w install links: [Grafana](http://docs.grafana.org/installation/), [Python3](https://www.python.org/downloads/), [InfluxDB](https://docs.influxdata.com/influxdb/v1.5/introduction/installation/)

<center><img width="800" src="https://i.imgur.com/av8e0HP.png"></center>

## Quick Setup (Varken Alpha)
1. Clone the repository `git clone https://github.com/DirtyCajunRice/grafana-scripts.git /opt/Varken`
1. Switch to the testing branch `cd /opt/Varken && git checkout refactor-project`
1. Install requirements `/usr/bin/python -m pip install -r requirements.txt`
2. Make a copy of `varken.example.ini` to `varken.ini` in the `data` folder
   `cp data/varken.example.ini data/varken.ini`
3. Make the appropriate changes to `varken.ini`
   `nano data/varken.ini`
4. Copy the systemd file `cp varken.service /etc/systemd/system/`
5. start the service and enable it `systemctl start varken && systemctl enable varken`
5. After completing the [getting started](http://docs.grafana.org/guides/getting_started/) portion of grafana, create your datasource for influxdb. At a minimum, you will need the plex database.
6. Install `grafana-cli plugins install grafana-worldmap-panel`
7. TODO:: Click the + on your menu and click import. Using the .json provided in this repo, paste it in and customize as you like.

