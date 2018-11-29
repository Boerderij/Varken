from typing import NamedTuple


class TVShow(NamedTuple):
    seriesId: int = None
    episodeFileId: int = None
    seasonNumber: int = None
    episodeNumber: int = None
    title: str = None
    airDate: str = None
    airDateUtc: str = None
    overview: str = None
    episodeFile: dict = None
    hasFile: bool = None
    monitored: bool = None
    unverifiedSceneNumbering: bool = None
    absoluteEpisodeNumber: int = None
    series: dict = None
    id: int = None


class Queue(NamedTuple):
    series: dict = None
    episode: dict = None
    quality: dict = None
    size: float = None
    title: str = None
    sizeleft: float = None
    timeleft: str = None
    estimatedCompletionTime: str = None
    status: str = None
    trackedDownloadStatus: str = None
    statusMessages: list = None
    downloadId: str = None
    protocol: str = None
    id: int = None


class Server(NamedTuple):
    id: int = None
    url: str = None
    api_key: str = None
    verify_ssl: bool = False


class TautulliServer(NamedTuple):
    url: str = None
    fallback_ip: str = None
    apikey: str = None
    verify_ssl: bool = None
    influx_db: str = None

class InfluxServer(NamedTuple):
    url: str = 'localhost'
    port: int = 8086
    username: str = 'root'
    password: str = 'root'