from typing import NamedTuple


class TVShow(NamedTuple):
    seriesId: int
    episodeFileId: int
    seasonNumber: int
    episodeNumber: int
    title: str
    airDate: str
    airDateUtc: str
    overview: str
    episodeFile: dict
    hasFile: bool
    monitored: bool
    unverifiedSceneNumbering: bool
    absoluteEpisodeNumber: int
    series: dict
    id: int


class Queue(NamedTuple):
    series: dict
    episode: dict
    quality: dict
    size: float
    title: str
    sizeleft: float
    timeleft: str
    estimatedCompletionTime: str
    status: str
    trackedDownloadStatus: str
    statusMessages: list
    downloadId: str
    protocol: str
    id: int


class Server(NamedTuple):
    url: str
    api_key: str
    id: int
