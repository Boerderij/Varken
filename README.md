# Grafana Scripts
Repo for api scripts written (both pushing and pulling) to aggregate data into influxdb for grafana

Requirements /w install links: [Grafana](http://docs.grafana.org/installation/), [Python3](https://www.python.org/downloads/), [InfluxDB](https://docs.influxdata.com/influxdb/v1.5/introduction/installation/)

## Quick Setup
1. Install requirements `pip3 install -r requirements.txt`
1. Make a copy of `configuration.example.py` to `configuration.py`
2. Make the appropriate changes to `configuration.py`
1. Create your plex database in influx
    ```sh
    user@server: ~$ influx
    > CREATE DATABASE plex
    > quit
    ```
1. After completing the [getting started](http://docs.grafana.org/guides/getting_started/) portion of grafana, create your datasource for influxdb. At a minimum, you will need the plex database.
1. Install `grafana-cli plugins install grafana-worldmap-panel`
1. Click the + on your menu and click import. Using the .json provided in this repo, paste it in and customize as you like.

## Scripts
### `sonarr.py`
Gathers data from Sonarr and pushes it to influxdb.

```
Script to aid in data gathering from Sonarr

optional arguments:
  -h, --help            show this help message and exit
  --missing             Get all missing TV shows
  --missing_days MISSING_DAYS
                        Get missing TV shows in past X days
  --upcoming            Get upcoming TV shows
  --future FUTURE       Get TV shows on X days into the future. Includes today.
                        i.e. --future 2 is Today and Tomorrow
  --queue               Get TV shows in queue
```
- Notes:
  - You cannot stack the arguments. ie. `sonarr.py --missing --queue`
  - One argument must be supplied

### `radarr.py`
Gathers data from Radarr and pushes it to influxdb

```
Script to aid in data gathering from Radarr

optional arguments:
  -h, --help     show this help message and exit
  --missing      Get missing movies
  --missing_avl  Get missing available movies
  --queue        Get movies in queue
```
- Notes:
  - You cannot stack the arguments. ie. `radarr.py --missing --queue`
  - One argument must be supplied
  - `--missing_avl` Refers to how Radarr has determined if the movie should be available to download. The easy way to determine if the movie will appear on this list is if the movie has a <span style="color:red">RED "Missing"</span> tag associated with that movie. <span style="color:blue">BLUE "Missing"</span> tag refers to a movie that is missing but is not available for download yet. These tags are determined by your "Minimum Availability" settings for that movie.

### `ombi.py`
Gathers data from Ombi and pushes it to influxdb

```
Script to aid in data gathering from Ombi

optional arguments:
  -h, --help  show this help message and exit
  --total     Get the total count of all requests
  --counts    Get the count of pending, approved, and available requests
```
- Notes:
  - You cannot stack the arguments. ie. `ombi.py --total --counts`
  - One argument must be supplied

### `tautulli.py`
Gathers data from Tautulli and pushes it to influxdb. On initial run it will download the geoip2 DB and use it for locations.

### `sickrage.py`
Gathers data from Sickrage and pushes it to influxdb

## Notes
To run the python scripts crontab is currently leveraged. Examples:
```sh
### Modify paths as appropriate. python3 is located in different places for different users. (`which python3` will give you the path)
### to edit your crontab entry, do not modify /var/spool/cron/crontabs/<user> directly, use `crontab -e`
### Crontabs require an empty line at the end or they WILL not run. Make sure to have 2 lines to be safe
### It is bad practice to run any cronjob more than once a minute. For timing help: https://crontab.guru/
* * * * * /usr/bin/python3 /path-to-grafana-scripts/ombi.py --total
* * * * * /usr/bin/python3 /path-to-grafana-scripts/tautulli.py
* * * * * /usr/bin/python3 /path-to-grafana-scripts/radarr.py --queue
* * * * * /usr/bin/python3 /path-to-grafana-scripts/sonarr.py --queue
*/30 * * * * /usr/bin/python3 /path-to-grafana-scripts/radarr.py --missing
*/30 * * * * /usr/bin/python3 /path-to-grafana-scripts/sonarr.py --missing
*/30 * * * * /usr/bin/python3 /path-to-grafana-scripts/sickrage.py
```
