# grafana-scripts
Repo for api scripts written (both pushing and pulling) to aggregate data into influxdb for grafana

Requirements: Grafana, Python3, InfluxDB

Install Grafana: http://docs.grafana.org/installation/
Install InfluxDB: https://docs.influxdata.com/influxdb/v1.5/introduction/installation/
Install python3: use your distro's package management tool or compile from source


After completing the getting started portion of grafana (http://docs.grafana.org/guides/getting_started/), create your datasource for influxdb. At a minimum, you will need the plex database.

Now, click the + on your menu and click import. Using the .json provided in this repo, paste it in and customize as you like.

To run the python scripts, I leverage crontab. I run tautulli and ombi every 30seconds and radarr/sickrage/sonarr/couchpotato every 30 minutes
