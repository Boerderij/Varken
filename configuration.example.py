'''
Notes:
    - Domains should be either http(s)://subdomain.domain.com or http(s)://domain.com/url_suffix

    - Sonarr + Radarr scripts support multiple servers. You can remove the second
      server by putting a # in front of the line.

    - tautulli_failback_ip, This is used when there is no IP listed in tautulli.
      This can happen when you are streaming locally. This is usually your public IP.
'''

########################### INFLUXDB CONFIG ###########################
influxdb_url = 'influxdb.domain.tld'
influxdb_port = 8086
influxdb_username = ''
influxdb_password = ''

############################ SONARR CONFIG ############################
sonarr_server_list =   [
    ('https://sonarr1.domain.tld', 'xxxxxxxxxxxxxxx', '1'),
    ('https://sonarr2.domain.tld', 'xxxxxxxxxxxxxxx', '2'),
    #('https://sonarr3.domain.tld', 'xxxxxxxxxxxxxxx', '3')
    ]
sonarr_influxdb_db_name = 'plex'

############################ RADARR CONFIG ############################
radarr_server_list =   [
    ('https://radarr1.domain.tld', 'xxxxxxxxxxxxxxx', '1'),
    ('https://radarr2.domain.tld', 'xxxxxxxxxxxxxxx', '2'),
    #('https://radarr3.domain.tld', 'xxxxxxxxxxxxxxx', '3')
    ]
radarr_influxdb_db_name = 'plex'

############################ OMBI CONFIG ##############################
ombi_url = 'https://ombi.domain.tld'
ombi_api_key = 'xxxxxxxxxxxxxxx'
ombi_influxdb_db_name = 'plex'

########################## TAUTULLI CONFIG ############################
tautulli_url = 'https://tautulli.domain.tld'
tautulli_api_key = 'xxxxxxxxxxxxxxx'
tautulli_failback_ip = ''
tautulli_influxdb_db_name = 'plex'

########################## FIREWALL CONFIG ############################
asa_url = 'https://firewall.domain.tld'
asa_username = 'cisco'
asa_password = 'cisco'
asa_influxdb_db_name = 'asa'

########################## SICKRAGE CONFIG ############################
sickrage_url = 'https://sickrage.domain.tld/'
sickrage_api_key = 'xxxxxxxxxxxxxxx'
sickrage_influxdb_db_name = 'plex'
