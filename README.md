# Varken
Dutch for PIG. PIG is an Acronym for Plex/InfluxDB/Grafana

Varken is a standalone commmand-line utility that will aggregate date
from the plex ecosystem into influxdb to be displayed in grafana

Requirements /w install links: [Grafana](http://docs.grafana.org/installation/), [Python3](https://www.python.org/downloads/), [InfluxDB](https://docs.influxdata.com/influxdb/v1.5/introduction/installation/)

<center><img width="800" src="https://i.imgur.com/av8e0HP.png"></center>

## Quick Setup (Varken Alpha)
1. Clone the repository `sudo git clone https://github.com/DirtyCajunRice/grafana-scripts.git /opt/Varken`
2. Change ownership to current user `sudo chown $USER -R /opt/Varken/`
1. Switch to the testing branch `cd /opt/Varken && git checkout refactor-project`
1. Create venv in project `/usr/bin/python3 -m venv varken-venv`
1. Install requirements `/opt/Varken/varken-venv/bin/python -m pip install -r requirements.txt`
2. Make a copy of `varken.example.ini` to `varken.ini` in the `data` folder
   `cp /opt/Varken/data/varken.example.ini /opt/Varken/data/varken.ini`
3. Make the appropriate changes to `varken.ini`
   `nano /opt/Varken/data/varken.ini`
4. Copy the systemd file `sudo cp /opt/Varken/varken.service /etc/systemd/system/`
1. Edit the username of the systemd file `sudo sed -i "s/username/$USER" /etc/systemd/system/varken.service`
5. start the service and enable it `systemctl start varken && systemctl enable varken`
5. After completing the [getting started](http://docs.grafana.org/guides/getting_started/) portion of grafana, create your datasource for influxdb. At a minimum, you will need the plex database.
6. Install `grafana-cli plugins install grafana-worldmap-panel`
7. TODO:: Click the + on your menu and click import. Using the .json provided in this repo, paste it in and customize as you like.

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