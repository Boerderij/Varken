# Varken
[![Build Status](https://travis-ci.org/Boerderij/Varken.svg?branch=master)](https://travis-ci.org/Boerderij/Varken)
[![Discord](https://img.shields.io/badge/Discord-Varken-7289DA.svg?logo=discord&style=flat-square)](https://discord.gg/AGTG44H)
[![BuyMeACoffee](https://img.shields.io/badge/BuyMeACoffee-Donate-ff813f.svg?logo=CoffeeScript&style=flat-square)](https://www.buymeacoffee.com/varken)

Dutch for PIG. PIG is an Acronym for Plex/InfluxDB/Grafana

Varken is a standalone command-line utility to aggregate data
from the Plex ecosystem into InfluxDB. Examples use Grafana for a
frontend

Requirements:
* Python3.6+
* Python3-pip
* InfluxDB

<p align="center">
<img width="800" src="https://i.imgur.com/av8e0HP.png">
</p>

## Quick Setup (Git Clone)
```
# Clone the repository
git clone https://github.com/Boerderij/Varken.git /opt/Varken

# Follow the systemd install instructions located in varken.systemd
cp /opt/Varken/varken.systemd /etc/systemd/system/varken.service
nano /etc/systemd/system/varken.service

# Create venv in project
/usr/bin/python3 -m venv /opt/Varken/varken-venv

# Install requirements
/opt/Varken/varken-venv/bin/python -m pip install -r requirements.txt

# Make a copy of varken.example.ini to varken.ini in the data folder
cp /opt/Varken/data/varken.example.ini /opt/Varken/data/varken.ini

# Make the appropriate changes to varken.ini
nano /opt/Varken/data/varken.ini

# Make sure all the files have the appropriate permissions
chown $USER:$USER -R /opt/Varken

# Start the service and enable it
systemctl start varken
systemctl enable varken
```
### Docker

[![Docker-Layers](https://images.microbadger.com/badges/image/boerderij/varken.svg)](https://microbadger.com/images/boerderij/varken")
[![Docker-Version](https://images.microbadger.com/badges/version/boerderij/varken.svg)](https://microbadger.com/images/boerderij/varken")
[![Docker Pulls](https://img.shields.io/docker/pulls/boerderij/varken.svg)](https://hub.docker.com/r/boerderij/varken/)
[![Docker Stars](https://img.shields.io/docker/stars/boerderij/varken.svg)](https://hub.docker.com/r/boerderij/varken/)
<details><summary>Example</summary>
<p>

```
docker run -d \
  --name=varken \
  -v <path to data>:/config \
  -e PGID=<gid> -e PUID=<uid> \
  -e TZ=America/Chicago \
  boerderij/varken
```
</p>
</details>

#### Tags
* **latest**
* **nightly**
* **release-tag** e.g. v1.0

#### Upgrading with docker
```sh
docker stop varken
docker rm varken
# Run deploy command above
```

### InfluxDB
[InfluxDB Installation Documentation](https://docs.influxdata.com/influxdb/v1.7/introduction/installation/)

Influxdb is required but not packaged as part of Varken. Varken will create
its database on its own. If you choose to give varken user permissions that
do not include database creation, please ensure you create an influx database
named `varken`

### Grafana
[Grafana Installation Documentation](http://docs.grafana.org/installation/)

Grafana is used in our examples but not required, nor packaged as part of
Varken. Panel example pictures are pinned in the grafana-panels channel of
discord. Future releases may contain a json-generator, but it does not exist
as varken stands today.