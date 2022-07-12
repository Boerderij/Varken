<p align="center">
<img width="800" src="https://raw.githubusercontent.com/Boerderij/Varken/master/assets/varken_full_banner.jpg" alt="Logo Banner">
</p>

[![pipeline status](https://img.shields.io/github/workflow/status/Boerderij/Varken/varken?style=flat-square)](https://github.com/Boerderij/Varken/actions?query=workflow%3Avarken)
[![Discord](https://img.shields.io/discord/518970285773422592.svg?colorB=7289DA&label=Discord&logo=Discord&logoColor=7289DA&style=flat-square)](https://discord.gg/VjZ6qSM)
[![ko-fi](https://img.shields.io/badge/Buy%20Us%20A%20Coffee-Donate-ff813f.svg?logo=CoffeeScript&style=flat-square)](https://ko-fi.com/varken)
[![Docker-Layers](https://images.microbadger.com/badges/image/boerderij/varken.svg)](https://microbadger.com/images/boerderij/varken)
[![Release](https://img.shields.io/github/release/boerderij/varken.svg?style=flat-square)](https://github.com/Boerderij/Varken/releases/latest)
[![Docker Pulls](https://img.shields.io/docker/pulls/boerderij/varken.svg)](https://hub.docker.com/r/boerderij/varken/)

Dutch for PIG. PIG is an Acronym for Plex/InfluxDB/Grafana

Varken is a standalone application to aggregate data from the Plex 
ecosystem into InfluxDB using Grafana for a frontend

Requirements:
* [Python 3.6.7+](https://www.python.org/downloads/release/python-367/)
* [Python3-pip](https://pip.pypa.io/en/stable/installing/)
* [InfluxDB 1.8.x](https://www.influxdata.com/)
* [Grafana](https://grafana.com/)

<p align="center">
Example Dashboard

<img width="800" src="https://i.imgur.com/3hNZTkC.png" alt="dashboard">
</p>

Supported Modules:
* [Sonarr](https://sonarr.tv/) - Smart PVR for newsgroup and bittorrent users.
* [SickChill](https://sickchill.github.io/) - SickChill is an automatic Video Library Manager for TV Shows.
* [Radarr](https://radarr.video/) - A fork of Sonarr to work with movies à la Couchpotato.
* [Tautulli](https://tautulli.com/) - A Python based monitoring and tracking tool for Plex Media Server.
* [Ombi](https://ombi.io/) - Want a Movie or TV Show on Plex or Emby? Use Ombi!
* [Lidarr](https://lidarr.audio/) - Looks and smells like Sonarr but made for music.

Key features:
* Multiple server support for all modules
* Geolocation mapping from [GeoLite2](https://dev.maxmind.com/geoip/geoip2/geolite2/)
* Grafana [Worldmap Panel](https://grafana.com/plugins/grafana-worldmap-panel/installation) support


## Installation Guides
Varken Installation guides can be found in the [wiki](https://wiki.cajun.pro/books/varken/chapter/installation).

## Support
Please read [Asking for Support](https://wiki.cajun.pro/books/varken/chapter/asking-for-support) before seeking support. 

[Click here for quick access to discord support](http://cyborg.decreator.dev/channels/518970285773422592/530424560504537105/). No app or account needed!
    
### InfluxDB
[InfluxDB Installation Documentation](https://wiki.cajun.pro/books/varken/page/influxdb-d1f)
Note: Only v1.8.x is currently supported.
 
Influxdb is required but not packaged as part of Varken. Varken will create
its database on its own. If you choose to give varken user permissions that
do not include database creation, please ensure you create an influx database
named `varken`

### Grafana
[Grafana Installation/Dashboard Documentation](https://wiki.cajun.pro/books/varken/page/grafana) 
