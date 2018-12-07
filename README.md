# Varken
[![Discord](https://img.shields.io/badge/Discord-Varken-7289DA.svg?logo=discord&style=flat-square)](https://discord.gg/AGTG44H)
[![BuyMeACoffee](https://img.shields.io/badge/BuyMeACoffee-Donate-ff813f.svg?logo=CoffeeScript&style=flat-square)](https://www.buymeacoffee.com/varken)
[![Docker Pulls](https://img.shields.io/docker/pulls/boerderij/varken.svg?style=flat-square)](https://hub.docker.com/r/boerderij/varken/)

Dutch for PIG. PIG is an Acronym for Plex/InfluxDB/Grafana

varken is a standalone command-line utility to aggregate data
from the Plex ecosystem into InfluxDB. Examples use Grafana for a
frontend

Requirements:
* Python3.6+
* Python3-pip

<p align="center">
<img width="800" src="https://i.imgur.com/av8e0HP.png">
</p>

## Quick Setup
1. Clone the repository `sudo git clone https://github.com/Boerderij/Varken.git /opt/Varken`
1. Follow the systemd install instructions located in `varken.systemd`
1. Create venv in project `cd /opt/Varken && /usr/bin/python3 -m venv varken-venv`
1. Install requirements `/opt/Varken/varken-venv/bin/python -m pip install -r requirements.txt`
1. Make a copy of `varken.example.ini` to `varken.ini` in the `data` folder
   `cp /opt/Varken/data/varken.example.ini /opt/Varken/data/varken.ini`
1. Make the appropriate changes to `varken.ini`
   ie.`nano /opt/Varken/data/varken.ini`
1. Make sure all the files have the appropriate permissions `sudo chown varken:varken -R /opt/Varken`
1. After completing the [getting started](http://docs.grafana.org/guides/getting_started/) portion of grafana, create your datasource for influxdb.
1. Install `grafana-cli plugins install grafana-worldmap-panel`

### Docker

Repo is included in [Boerderij/docker-Varken](https://github.com/Boerderij/docker-Varken)

<details><summary>Example</summary>
<p>

```
docker run -d \
  --name=varken \
  -v <path to data>:/config \
  -e PGID=<gid> -e PUID=<uid>  \
  boerderij/varken:nightly
```
</p>
</details>
