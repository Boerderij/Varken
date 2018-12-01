import os
import time
import tarfile
import geoip2.database
from typing import NamedTuple
from os.path import abspath, join
from urllib.request import urlretrieve


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


class SonarrServer(NamedTuple):
    id: int = None
    url: str = None
    api_key: str = None
    verify_ssl: bool = False
    missing_days: int = 0
    missing_days_run_seconds: int = 30
    future_days: int = 0
    future_days_run_seconds: int = 30
    queue: bool = False
    queue_run_seconds: int = 1


class Server(NamedTuple):
    id: int = None
    url: str = None
    api_key: str = None
    verify_ssl: bool = False


class TautulliServer(NamedTuple):
    id: int = None
    url: str = None
    fallback_ip: str = None
    apikey: str = None
    verify_ssl: bool = None
    get_activity: bool = False
    get_activity_run_seconds: int = 30
    get_sessions: bool = False
    get_sessions_run_seconds: int = 30


class InfluxServer(NamedTuple):
    url: str = 'localhost'
    port: int = 8086
    username: str = 'root'
    password: str = 'root'


class TautulliStream(NamedTuple):
    rating: str
    transcode_width: str
    labels: list
    stream_bitrate: str
    bandwidth: str
    optimized_version: int
    video_language: str
    parent_rating_key: str
    rating_key: str
    platform_version: str
    transcode_hw_decoding: int
    thumb: str
    title: str
    video_codec_level: str
    tagline: str
    last_viewed_at: str
    audio_sample_rate: str
    user_rating: str
    platform: str
    collections: list
    location: str
    transcode_container: str
    audio_channel_layout: str
    local: str
    stream_subtitle_format: str
    stream_video_ref_frames: str
    transcode_hw_encode_title: str
    stream_container_decision: str
    audience_rating: str
    full_title: str
    ip_address: str
    subtitles: int
    stream_subtitle_language: str
    channel_stream: int
    video_bitrate: str
    is_allow_sync: int
    stream_video_bitrate: str
    summary: str
    stream_audio_decision: str
    aspect_ratio: str
    audio_bitrate_mode: str
    transcode_hw_decode_title: str
    stream_audio_channel_layout: str
    deleted_user: int
    library_name: str
    art: str
    stream_video_resolution: str
    video_profile: str
    sort_title: str
    stream_video_codec_level: str
    stream_video_height: str
    year: str
    stream_duration: str
    stream_audio_channels: str
    video_language_code: str
    transcode_key: str
    transcode_throttled: int
    container: str
    stream_audio_bitrate: str
    user: str
    selected: int
    product_version: str
    subtitle_location: str
    transcode_hw_requested: int
    video_height: str
    state: str
    is_restricted: int
    email: str
    stream_container: str
    transcode_speed: str
    video_bit_depth: str
    stream_audio_sample_rate: str
    grandparent_title: str
    studio: str
    transcode_decision: str
    video_width: str
    bitrate: str
    machine_id: str
    originally_available_at: str
    video_frame_rate: str
    synced_version_profile: str
    friendly_name: str
    audio_profile: str
    optimized_version_title: str
    platform_name: str
    stream_video_language: str
    keep_history: int
    stream_audio_codec: str
    stream_video_codec: str
    grandparent_thumb: str
    synced_version: int
    transcode_hw_decode: str
    user_thumb: str
    stream_video_width: str
    height: str
    stream_subtitle_decision: str
    audio_codec: str
    parent_title: str
    guid: str
    audio_language_code: str
    transcode_video_codec: str
    transcode_audio_codec: str
    stream_video_decision: str
    user_id: int
    transcode_height: str
    transcode_hw_full_pipeline: int
    throttled: str
    quality_profile: str
    width: str
    live: int
    stream_subtitle_forced: int
    media_type: str
    video_resolution: str
    stream_subtitle_location: str
    do_notify: int
    video_ref_frames: str
    stream_subtitle_language_code: str
    audio_channels: str
    stream_audio_language_code: str
    optimized_version_profile: str
    relay: int
    duration: str
    rating_image: str
    is_home_user: int
    is_admin: int
    ip_address_public: str
    allow_guest: int
    transcode_audio_channels: str
    stream_audio_channel_layout_: str
    media_index: str
    stream_video_framerate: str
    transcode_hw_encode: str
    grandparent_rating_key: str
    original_title: str
    added_at: str
    banner: str
    bif_thumb: str
    parent_media_index: str
    live_uuid: str
    audio_language: str
    stream_audio_bitrate_mode: str
    username: str
    subtitle_decision: str
    children_count: str
    updated_at: str
    player: str
    subtitle_format: str
    file: str
    file_size: str
    session_key: str
    id: str
    subtitle_container: str
    genres: list
    stream_video_language_code: str
    indexes: int
    video_decision: str
    stream_audio_language: str
    writers: list
    actors: list
    progress_percent: str
    audio_decision: str
    subtitle_forced: int
    profile: str
    product: str
    view_offset: str
    type: str
    audience_rating_image: str
    audio_bitrate: str
    section_id: str
    stream_subtitle_codec: str
    subtitle_codec: str
    video_codec: str
    device: str
    stream_video_bit_depth: str
    video_framerate: str
    transcode_hw_encoding: int
    transcode_protocol: str
    shared_libraries: list
    stream_aspect_ratio: str
    content_rating: str
    session_id: str
    directors: list
    parent_thumb: str
    subtitle_language_code: str
    transcode_progress: int
    subtitle_language: str
    stream_subtitle_container: str

def geoip_download():
    tar_dbfile = abspath(join('..', 'data', 'GeoLite2-City.tar.gz'))
    url = 'http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz'
    urlretrieve(url, tar_dbfile)
    tar = tarfile.open(tar_dbfile, "r:gz")
    for files in tar.getmembers():
        if 'GeoLite2-City.mmdb' in files.name:
            files.name = os.path.basename(files.name)
            tar.extract(files, '{}/'.format(os.path.dirname(os.path.realpath(__file__))))
    os.remove(tar_dbfile)

def geo_lookup(ipaddress):

    dbfile = abspath(join('..', 'data', 'GeoLite2-City.mmdb'))
    now = time.time()

    try:
        dbinfo = os.stat(dbfile)
        db_age = now - dbinfo.st_ctime
        if db_age > (35 * 86400):
            os.remove(dbfile)
            geoip_download()
    except FileNotFoundError:
        geoip_download()

    reader = geoip2.database.Reader(dbfile)

    return reader.city(ipaddress)
