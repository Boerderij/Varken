# Grafana Scripts
Repo for api scripts written (both pushing and pulling) to aggregate data into influxdb for grafana

Requirements /w install links: [Grafana](http://docs.grafana.org/installation/), [Python3](https://www.python.org/downloads/), [InfluxDB](https://docs.influxdata.com/influxdb/v1.5/introduction/installation/)

## Quick Setup
1. Install requirements
2. Create your plex database in influx
    ```sh
    user@server: ~$ influx
    > CREATE DATABASE plex
    > quit
    ```
3. After completing the [getting started](http://docs.grafana.org/guides/getting_started/) portion of grafana, create your datasource for influxdb. At a minimum, you will need the plex database.
4. Click the + on your menu and click import. Using the .json provided in this repo, paste it in and customize as you like.

## Notes
To run the python scripts, I leverage crontab. I run tautulli and ombi every 30seconds and radarr/sickrage/sonarr/couchpotato every 30 minutes
