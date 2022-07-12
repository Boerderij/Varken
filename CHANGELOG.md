# Change Log

## [v1.7.7](https://github.com/Boerderij/Varken/tree/v1.7.7) (2020-12-21)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.7.6...v1.7.7)

**Implemented enhancements:**
- \[Enhancement\] Ombi 4.0 compatibility [\#186](https://github.com/Boerderij/Varken/issues/186)
  ([samwiseg0](https://github.com/samwiseg0))

**Merged pull requests:**

- v1.7.7 Merge [\#191](https://github.com/Boerderij/Varken/pull/191) 
  ([DirtyCajunRice](https://github.com/DirtyCajunRice))
- Type Error fix [\#177](https://github.com/Boerderij/Varken/pull/177)
  ([derek-miller](https://github.com/derek-miller))

**Fixed bugs:**

- \[BUG\] Influxdb exit code [\#174](https://github.com/Boerderij/Varken/issues/174) 
  ([samwiseg0](https://github.com/samwiseg0))

**Notes:**
- Now built via github actions
- Available on ghcr, quay.io, and dockerhub
- Nightly builds done to accommodate dependabot MRs

## [v1.7.6](https://github.com/Boerderij/Varken/tree/v1.7.6) (2020-01-01)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.7.5...v1.7.6)

**Merged pull requests:**

- v1.7.6 Merge [\#165](https://github.com/Boerderij/Varken/pull/165) ([samwiseg0](https://github.com/samwiseg0))

**Fixed bugs:**

- \[BUG\] Geolite database download failing [\#164](https://github.com/Boerderij/Varken/issues/164)

**Notes:**
- A MaxMind license key will be required in order to download the GeoLite2 DB. Please see the [wiki](https://wiki.cajun.pro/link/5#bkmrk-maxmind) for more details.

## [v1.7.5](https://github.com/Boerderij/Varken/tree/v1.7.5) (2019-12-11)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.7.4...v1.7.5)

**Merged pull requests:**

- v1.7.5 Merge [\#162](https://github.com/Boerderij/Varken/pull/162) ([DirtyCajunRice](https://github.com/DirtyCajunRice))
- Add helper itemgetter function for TautulliStream fields [\#157](https://github.com/Boerderij/Varken/pull/157) ([JonnyWong16](https://github.com/JonnyWong16))
- Fix to only use NamedTuple fields from TautulliStream [\#156](https://github.com/Boerderij/Varken/pull/156) ([JonnyWong16](https://github.com/JonnyWong16))

## [1.7.4](https://github.com/Boerderij/Varken/tree/1.7.4) (2019-10-07)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.7.3...1.7.4)

**Implemented enhancements:**

- \[Enhancement\] Update Tautulli structures to include grandparent\_guid and parent\_guid [\#154](https://github.com/Boerderij/Varken/issues/154)
- \[Enhancement\] Update Tautulli structures to reflect recent changes [\#153](https://github.com/Boerderij/Varken/issues/153)

**Merged pull requests:**

- v1.7.4 Merge [\#155](https://github.com/Boerderij/Varken/pull/155) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [1.7.3](https://github.com/Boerderij/Varken/tree/1.7.3) (2019-08-09)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.7.2...1.7.3)

**Implemented enhancements:**

- \#141 Take monitored status into account for Missing Available Movies check [\#145](https://github.com/Boerderij/Varken/pull/145) ([mikeporterdev](https://github.com/mikeporterdev))

**Fixed bugs:**

- \[BUG\] Varken Crashes when ini is read only [\#146](https://github.com/Boerderij/Varken/issues/146)
- \[BUG\] Missing Available Movies/TV Shows does not take Monitored status into account [\#141](https://github.com/Boerderij/Varken/issues/141)

**Closed issues:**

- \[Feature Request\] Medusa Support [\#148](https://github.com/Boerderij/Varken/issues/148)

**Merged pull requests:**

- v1.7.3 Merge [\#149](https://github.com/Boerderij/Varken/pull/149) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [1.7.2](https://github.com/Boerderij/Varken/tree/1.7.2) (2019-06-24)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.7.1...1.7.2)

**Implemented enhancements:**

- Allow configuration via environment variables [\#137](https://github.com/Boerderij/Varken/issues/137)

**Fixed bugs:**

- \[BUG\] logger invoked before initialization in dbmanager [\#138](https://github.com/Boerderij/Varken/issues/138)

**Merged pull requests:**

- v1.7.2 Merge [\#144](https://github.com/Boerderij/Varken/pull/144) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [1.7.1](https://github.com/Boerderij/Varken/tree/1.7.1) (2019-06-04)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.7.0...1.7.1)

**Fixed bugs:**

- \[BUG\] Sonarr Missing episodes column ordering is incorrect [\#133](https://github.com/Boerderij/Varken/pull/133) ([nicolerenee](https://github.com/nicolerenee))

**Merged pull requests:**

- v1.7.1 Merge [\#134](https://github.com/Boerderij/Varken/pull/134) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [1.7.0](https://github.com/Boerderij/Varken/tree/1.7.0) (2019-05-06)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.6.8...1.7.0)

**Implemented enhancements:**

- \[ENHANCEMENT\] Add album and track totals to artist library from Tautulli [\#127](https://github.com/Boerderij/Varken/issues/127)
- \[Feature Request\] No way to show music album / track count [\#125](https://github.com/Boerderij/Varken/issues/125)

**Fixed bugs:**

- \[BUG\] Invalid retention policy name causing retention policy creation failure [\#129](https://github.com/Boerderij/Varken/issues/129)
- \[BUG\] Unifi errors on unnamed devices [\#126](https://github.com/Boerderij/Varken/issues/126)

**Merged pull requests:**

- v1.7.0 Merge [\#131](https://github.com/Boerderij/Varken/pull/131) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [1.6.8](https://github.com/Boerderij/Varken/tree/1.6.8) (2019-04-19)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.6.7...1.6.8)

**Implemented enhancements:**

- \[Enhancement\] Only drop the invalid episodes from sonarr [\#121](https://github.com/Boerderij/Varken/issues/121)

**Merged pull requests:**

- v1.6.8 Merge [\#122](https://github.com/Boerderij/Varken/pull/122) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [1.6.7](https://github.com/Boerderij/Varken/tree/1.6.7) (2019-04-18)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.6.6...1.6.7)

**Implemented enhancements:**

- \[BUG\] Ombi null childRequest output [\#119](https://github.com/Boerderij/Varken/issues/119)
- \[ENHANCEMENT\] Invalid entries in Sonarr's queue leaves varken unable to process the rest of the queue [\#117](https://github.com/Boerderij/Varken/issues/117)

**Merged pull requests:**

- v1.6.7 Merge [\#120](https://github.com/Boerderij/Varken/pull/120) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [1.6.6](https://github.com/Boerderij/Varken/tree/1.6.6) (2019-03-12)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.6.5...1.6.6)

**Fixed bugs:**

- \[BUG\] TZDATA issue in docker images [\#112](https://github.com/Boerderij/Varken/issues/112)
- \[BUG\] Unifi job does not try again after failure [\#107](https://github.com/Boerderij/Varken/issues/107)
- \[BUG\] Catch ChunkError [\#106](https://github.com/Boerderij/Varken/issues/106)

**Merged pull requests:**

- v1.6.6 Merge [\#116](https://github.com/Boerderij/Varken/pull/116) ([samwiseg0](https://github.com/samwiseg0))

## [1.6.5](https://github.com/Boerderij/Varken/tree/1.6.5) (2019-03-11)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.6.4...1.6.5)

**Implemented enhancements:**

- \[Feature Request\] Add new "relayed" and "secure" to Tautulli data pushed to influx [\#114](https://github.com/Boerderij/Varken/issues/114)
- \[BUG\] Changes to Tautulli breaks Varken `TypeError` `Secure` `relayed` [\#111](https://github.com/Boerderij/Varken/issues/111)

**Fixed bugs:**

- \[BUG\] Handle GeoIP Downloads better [\#113](https://github.com/Boerderij/Varken/issues/113)
- \[BUG\] - "None" outputted to stdout many times with no benefit? [\#105](https://github.com/Boerderij/Varken/issues/105)
- \[BUG\] windows file open error [\#104](https://github.com/Boerderij/Varken/issues/104)
- \[BUG\] Not catching DB url resolve [\#103](https://github.com/Boerderij/Varken/issues/103)

**Merged pull requests:**

- v1.6.5 Merge [\#115](https://github.com/Boerderij/Varken/pull/115) ([samwiseg0](https://github.com/samwiseg0))

## [v1.6.4](https://github.com/Boerderij/Varken/tree/v1.6.4) (2019-02-04)
[Full Changelog](https://github.com/Boerderij/Varken/compare/1.6.3...v1.6.4)

**Fixed bugs:**

- \[BUG\] fstring in Varken.py Doesnt allow py version check [\#102](https://github.com/Boerderij/Varken/issues/102)
- \[BUG\] Unifi loadavg is str instead of float [\#101](https://github.com/Boerderij/Varken/issues/101)
- \[BUG\] requestedByAlias to added to Ombi structures  [\#97](https://github.com/Boerderij/Varken/issues/97)

**Merged pull requests:**

- v1.6.4 Merge [\#100](https://github.com/Boerderij/Varken/pull/100) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [1.6.3](https://github.com/Boerderij/Varken/tree/1.6.3) (2019-01-16)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.6.2...1.6.3)

**Implemented enhancements:**

- \[Feature Request\] ARM, ARMHF and ARM64 Docker Images [\#71](https://github.com/Boerderij/Varken/issues/71)

**Fixed bugs:**

- \[BUG\] Newer influxdb has timeouts and connection errors [\#93](https://github.com/Boerderij/Varken/issues/93)

**Merged pull requests:**

- double typo [\#96](https://github.com/Boerderij/Varken/pull/96) ([DirtyCajunRice](https://github.com/DirtyCajunRice))
- tweaks [\#95](https://github.com/Boerderij/Varken/pull/95) ([DirtyCajunRice](https://github.com/DirtyCajunRice))
- v1.6.3 Merge [\#94](https://github.com/Boerderij/Varken/pull/94) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v1.6.2](https://github.com/Boerderij/Varken/tree/v1.6.2) (2019-01-12)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.6.1...v1.6.2)

**Fixed bugs:**

- Rectify influxdb ini [\#91](https://github.com/Boerderij/Varken/issues/91)

**Merged pull requests:**

- v1.6.2 Merge [\#92](https://github.com/Boerderij/Varken/pull/92) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v1.6.1](https://github.com/Boerderij/Varken/tree/v1.6.1) (2019-01-12)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.6...v1.6.1)

**Implemented enhancements:**

- \[Feature Request\] Unifi Integration [\#79](https://github.com/Boerderij/Varken/issues/79)

**Fixed bugs:**

- \[BUG\] Unexpected keyword argument 'langCode' while creating OmbiMovieRequest structure [\#88](https://github.com/Boerderij/Varken/issues/88)

**Closed issues:**

- Remove Cisco ASA since Telegraf + SNMP can do the same [\#86](https://github.com/Boerderij/Varken/issues/86)

**Merged pull requests:**

- v1.6.1 Merge [\#90](https://github.com/Boerderij/Varken/pull/90) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v1.6](https://github.com/Boerderij/Varken/tree/v1.6) (2019-01-04)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.5...v1.6)

**Implemented enhancements:**

- \[Feature Request\] docker-compose stack install option [\#84](https://github.com/Boerderij/Varken/issues/84)
- Fix missing variables in varken.ini automatically [\#81](https://github.com/Boerderij/Varken/issues/81)
- Create Wiki for FAQ and help docs [\#80](https://github.com/Boerderij/Varken/issues/80)

**Fixed bugs:**

- \[BUG\] url:port does not filter [\#82](https://github.com/Boerderij/Varken/issues/82)

**Merged pull requests:**

- v1.6 Merge [\#85](https://github.com/Boerderij/Varken/pull/85) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v1.5](https://github.com/Boerderij/Varken/tree/v1.5) (2018-12-30)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.4...v1.5)

**Implemented enhancements:**

- \[Feature Request\] Add issues from Ombi [\#70](https://github.com/Boerderij/Varken/issues/70)
- Replace static grafana configs with a Public Example [\#32](https://github.com/Boerderij/Varken/issues/32)

**Fixed bugs:**

- \[BUG\] unexpected keyword argument 'channel\_icon' [\#73](https://github.com/Boerderij/Varken/issues/73)
- \[BUG\] Unexpected keyword argument 'addOptions'  [\#68](https://github.com/Boerderij/Varken/issues/68)

**Merged pull requests:**

- v1.5 Merge [\#75](https://github.com/Boerderij/Varken/pull/75) ([DirtyCajunRice](https://github.com/DirtyCajunRice))
- Add Ombi Issues [\#74](https://github.com/Boerderij/Varken/pull/74) ([anderssonoscar0](https://github.com/anderssonoscar0))

## [v1.4](https://github.com/Boerderij/Varken/tree/v1.4) (2018-12-19)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.1...v1.4)

**Implemented enhancements:**

- \[Feature Request\] Add tautulli request for library stats [\#64](https://github.com/Boerderij/Varken/issues/64)
- Create randomized 12-24 hour checks to update GeoLite DB after the first wednesday of the month [\#60](https://github.com/Boerderij/Varken/issues/60)
- \[Feature Request\]: Pull list of requests \(instead of just counts\) [\#58](https://github.com/Boerderij/Varken/issues/58)
- Feature Request  , Add Sickchill [\#48](https://github.com/Boerderij/Varken/issues/48)

**Fixed bugs:**

- \[BUG\] Ombi all requests missing half of "pending" option [\#63](https://github.com/Boerderij/Varken/issues/63)
- \[BUG\] asa bug with checking for apikey [\#62](https://github.com/Boerderij/Varken/issues/62)
- \[BUG\] Add Catchall to ombi requests [\#59](https://github.com/Boerderij/Varken/issues/59)

**Closed issues:**

- Unify naming and cleanup duplication in iniparser [\#61](https://github.com/Boerderij/Varken/issues/61)

**Merged pull requests:**

- v1.4 Merge [\#65](https://github.com/Boerderij/Varken/pull/65) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v1.1](https://github.com/Boerderij/Varken/tree/v1.1) (2018-12-11)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.0...v1.1)

**Implemented enhancements:**

- Convert missing available to True False  [\#54](https://github.com/Boerderij/Varken/issues/54)
- Handle invalid config better and log it [\#51](https://github.com/Boerderij/Varken/issues/51)
- Feature Request - Include value from Radarr [\#50](https://github.com/Boerderij/Varken/issues/50)
- Change true/false to 0/1 for missing movies [\#47](https://github.com/Boerderij/Varken/issues/47)

**Fixed bugs:**

- \[BUG\] Time does not update from "today" [\#56](https://github.com/Boerderij/Varken/issues/56)
- geoip\_download does not account for moving data folder [\#46](https://github.com/Boerderij/Varken/issues/46)

**Closed issues:**

- Initial startup requires admin access to InfluxDB [\#53](https://github.com/Boerderij/Varken/issues/53)

**Merged pull requests:**

- v1.1 Merge [\#57](https://github.com/Boerderij/Varken/pull/57) ([DirtyCajunRice](https://github.com/DirtyCajunRice))
- Update issue templates [\#55](https://github.com/Boerderij/Varken/pull/55) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v1.0](https://github.com/Boerderij/Varken/tree/v1.0) (2018-12-10)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v0.1...v1.0)

**Implemented enhancements:**

- Add cisco asa from legacy [\#44](https://github.com/Boerderij/Varken/issues/44)
- Add server ID to ombi to differenciate [\#43](https://github.com/Boerderij/Varken/issues/43)
- Create Changelog for nightly release [\#39](https://github.com/Boerderij/Varken/issues/39)
- Create proper logging [\#34](https://github.com/Boerderij/Varken/issues/34)

**Closed issues:**

- Remove "dashboard" folder and subfolders [\#42](https://github.com/Boerderij/Varken/issues/42)
- Remove "Legacy" folder [\#41](https://github.com/Boerderij/Varken/issues/41)
- Create the DB if it does not exist. [\#38](https://github.com/Boerderij/Varken/issues/38)
- create systemd examples [\#37](https://github.com/Boerderij/Varken/issues/37)
- Create a GeoIP db downloader and refresher [\#36](https://github.com/Boerderij/Varken/issues/36)
- Create unique IDs for all scripts to prevent duplicate data [\#35](https://github.com/Boerderij/Varken/issues/35)
- use a config.ini instead of command-line flags [\#33](https://github.com/Boerderij/Varken/issues/33)
- Migrate crontab to python schedule package [\#31](https://github.com/Boerderij/Varken/issues/31)
- Consolidate missing and missing\_days in sonarr.py [\#30](https://github.com/Boerderij/Varken/issues/30)
- Ombi something new \[Request\] [\#26](https://github.com/Boerderij/Varken/issues/26)
- Support for Linux without ASA [\#21](https://github.com/Boerderij/Varken/issues/21)

**Merged pull requests:**

- v1.0 Merge [\#45](https://github.com/Boerderij/Varken/pull/45) ([DirtyCajunRice](https://github.com/DirtyCajunRice))
- varken to nightly [\#40](https://github.com/Boerderij/Varken/pull/40) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v0.1](https://github.com/Boerderij/Varken/tree/v0.1) (2018-10-20)
**Implemented enhancements:**

- The address 172.17.0.1 is not in the database. [\#17](https://github.com/Boerderij/Varken/issues/17)
- Local streams aren't showing with Tautulli [\#16](https://github.com/Boerderij/Varken/issues/16)
- Worldmap panel [\#15](https://github.com/Boerderij/Varken/issues/15)

**Closed issues:**

- Issues with scripts [\#12](https://github.com/Boerderij/Varken/issues/12)
- issue with new tautulli.py [\#10](https://github.com/Boerderij/Varken/issues/10)
- ombi.py fails when attempting to update influxdb [\#9](https://github.com/Boerderij/Varken/issues/9)
- GeoIP Going to Break July 1st [\#8](https://github.com/Boerderij/Varken/issues/8)
- \[Request\] Documentation / How-to Guide [\#1](https://github.com/Boerderij/Varken/issues/1)

**Merged pull requests:**

- v0.1 [\#20](https://github.com/Boerderij/Varken/pull/20) ([samwiseg0](https://github.com/samwiseg0))
- Added selfplug [\#19](https://github.com/Boerderij/Varken/pull/19) ([Roxedus](https://github.com/Roxedus))
- Major rework of the scripts [\#14](https://github.com/Boerderij/Varken/pull/14) ([samwiseg0](https://github.com/samwiseg0))
- fix worldmap after change to maxmind local db [\#11](https://github.com/Boerderij/Varken/pull/11) ([madbuda](https://github.com/madbuda))
- Update sonarr.py [\#7](https://github.com/Boerderij/Varken/pull/7) ([ghost](https://github.com/ghost))
- Create crontabs [\#6](https://github.com/Boerderij/Varken/pull/6) ([ghost](https://github.com/ghost))
- update plex\_dashboard.json [\#5](https://github.com/Boerderij/Varken/pull/5) ([ghost](https://github.com/ghost))
- Update README.md [\#4](https://github.com/Boerderij/Varken/pull/4) ([ghost](https://github.com/ghost))
- added sickrage portion [\#3](https://github.com/Boerderij/Varken/pull/3) ([ghost](https://github.com/ghost))
