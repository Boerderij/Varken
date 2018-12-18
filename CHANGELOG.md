# Change Log

## [v1.3-nightly](https://github.com/Boerderij/Varken/tree/v1.3-nightly) (2018-12-17)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.2-nightly...v1.3-nightly)

**Implemented enhancements:**

- Create randomized 12-24 hour checks to update GeoLite DB after the first wednesday of the month [\#60](https://github.com/Boerderij/Varken/issues/60)

**Fixed bugs:**

- \[BUG\] Add Catchall to ombi requests [\#59](https://github.com/Boerderij/Varken/issues/59)

**Closed issues:**

- Unify naming and cleanup duplication in iniparser [\#61](https://github.com/Boerderij/Varken/issues/61)

## [v1.2-nightly](https://github.com/Boerderij/Varken/tree/v1.2-nightly) (2018-12-16)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v1.1...v1.2-nightly)

**Implemented enhancements:**

- \[Feature Request\]: Pull list of requests \(instead of just counts\) [\#58](https://github.com/Boerderij/Varken/issues/58)
- Feature Request  , Add Sickchill [\#48](https://github.com/Boerderij/Varken/issues/48)

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
- Ability to add custom tautulli port [\#49](https://github.com/Boerderij/Varken/issues/49)

**Merged pull requests:**

- v1.1 Merge [\#57](https://github.com/Boerderij/Varken/pull/57) ([DirtyCajunRice](https://github.com/DirtyCajunRice))
- Update issue templates [\#55](https://github.com/Boerderij/Varken/pull/55) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v1.0](https://github.com/Boerderij/Varken/tree/v1.0) (2018-12-10)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v0.3-nightly...v1.0)

**Implemented enhancements:**

- Add cisco asa from legacy [\#44](https://github.com/Boerderij/Varken/issues/44)
- Add server ID to ombi to differenciate [\#43](https://github.com/Boerderij/Varken/issues/43)

**Merged pull requests:**

- v1.0 Merge [\#45](https://github.com/Boerderij/Varken/pull/45) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v0.3-nightly](https://github.com/Boerderij/Varken/tree/v0.3-nightly) (2018-12-07)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v0.2-nightly...v0.3-nightly)

**Implemented enhancements:**

- Create Changelog for nightly release [\#39](https://github.com/Boerderij/Varken/issues/39)
- Create proper logging [\#34](https://github.com/Boerderij/Varken/issues/34)

**Closed issues:**

- Remove "dashboard" folder and subfolders [\#42](https://github.com/Boerderij/Varken/issues/42)
- Remove "Legacy" folder [\#41](https://github.com/Boerderij/Varken/issues/41)

## [v0.2-nightly](https://github.com/Boerderij/Varken/tree/v0.2-nightly) (2018-12-06)
[Full Changelog](https://github.com/Boerderij/Varken/compare/v0.1...v0.2-nightly)

**Implemented enhancements:**

- Tautulli - multiple server support? [\#25](https://github.com/Boerderij/Varken/issues/25)

**Closed issues:**

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

- varken to nightly [\#40](https://github.com/Boerderij/Varken/pull/40) ([DirtyCajunRice](https://github.com/DirtyCajunRice))

## [v0.1](https://github.com/Boerderij/Varken/tree/v0.1) (2018-10-20)
**Implemented enhancements:**

- The address 172.17.0.1 is not in the database. [\#17](https://github.com/Boerderij/Varken/issues/17)
- Local streams aren't showing with Tautulli [\#16](https://github.com/Boerderij/Varken/issues/16)
- Worldmap panel [\#15](https://github.com/Boerderij/Varken/issues/15)

**Closed issues:**

- Tautulli.py not working. [\#18](https://github.com/Boerderij/Varken/issues/18)
- Issues with scripts [\#12](https://github.com/Boerderij/Varken/issues/12)
- issue with new tautulli.py [\#10](https://github.com/Boerderij/Varken/issues/10)
- ombi.py fails when attempting to update influxdb [\#9](https://github.com/Boerderij/Varken/issues/9)
- GeoIP Going to Break July 1st [\#8](https://github.com/Boerderij/Varken/issues/8)
- \[Request\] Documentation / How-to Guide [\#1](https://github.com/Boerderij/Varken/issues/1)

**Merged pull requests:**

- v0.1 [\#20](https://github.com/Boerderij/Varken/pull/20) ([samwiseg0](https://github.com/samwiseg0))
- Added selfplug [\#19](https://github.com/Boerderij/Varken/pull/19) ([si0972](https://github.com/si0972))
- Major rework of the scripts [\#14](https://github.com/Boerderij/Varken/pull/14) ([samwiseg0](https://github.com/samwiseg0))
- fix worldmap after change to maxmind local db [\#11](https://github.com/Boerderij/Varken/pull/11) ([madbuda](https://github.com/madbuda))
- Update sonarr.py [\#7](https://github.com/Boerderij/Varken/pull/7) ([ghost](https://github.com/ghost))
- Create crontabs [\#6](https://github.com/Boerderij/Varken/pull/6) ([ghost](https://github.com/ghost))
- update plex\_dashboard.json [\#5](https://github.com/Boerderij/Varken/pull/5) ([ghost](https://github.com/ghost))
- Update README.md [\#4](https://github.com/Boerderij/Varken/pull/4) ([ghost](https://github.com/ghost))
- added sickrage portion [\#3](https://github.com/Boerderij/Varken/pull/3) ([ghost](https://github.com/ghost))
