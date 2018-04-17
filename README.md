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
To run the python scripts crontab is currently leveraged. Examples:
```sh
### Modify paths as appropriate. python3 is located in different places for different users. (`which python3` will give you the path)
### to edit your crontab entry, do not modify /var/spool/cron/crontabs/<user> directly, use `crontab -e`
### Crontabs require an empty line at the end or they WILL not run. Make sure to have 2 lines to be safe
### It is bad practice to run any cronjob more than once a minute. For timing help: https://crontab.guru/
* * * * * /usr/bin/python3 /path-to-grafana-scripts/ombi.py
* * * * * /usr/bin/python3 /path-to-grafana-scripts/tautulli.py
*/30 * * * * /usr/bin/python3 /path-to-grafana-scripts/radarr.py
*/30 * * * * /usr/bin/python3 /path-to-grafana-scripts/sonarr.py
*/30 * * * * /usr/bin/python3 /path-to-grafana-scripts/sickrage.py
```
