from sys import version_info
from typing import NamedTuple
from logging import getLogger

logger = getLogger('temp')
# Check for python3.6 or newer to resolve erroneous typing.NamedTuple issues
if version_info < (3, 6, 2):
    logger.error('Varken requires python3.6.2 or newer. You are on python%s.%s.%s - Exiting...',
                 version_info.major, version_info.minor, version_info.micro)
    exit(1)


# Server Structures
class InfluxServer(NamedTuple):
    password: str = 'root'
    port: int = 8086
    url: str = 'localhost'
    username: str = 'root'


class SonarrServer(NamedTuple):
    api_key: str = None
    future_days: int = 0
    future_days_run_seconds: int = 30
    id: int = None
    missing_days: int = 0
    missing_days_run_seconds: int = 30
    queue: bool = False
    queue_run_seconds: int = 30
    url: str = None
    verify_ssl: bool = False


class RadarrServer(NamedTuple):
    api_key: str = None
    get_missing: bool = False
    get_missing_run_seconds: int = 30
    id: int = None
    queue: bool = False
    queue_run_seconds: int = 30
    url: str = None
    verify_ssl: bool = False


class OmbiServer(NamedTuple):
    api_key: str = None
    id: int = None
    issue_status_counts: bool = False
    issue_status_run_seconds: int = 30
    request_total_counts: bool = False
    request_total_run_seconds: int = 30
    request_type_counts: bool = False
    request_type_run_seconds: int = 30
    url: str = None
    verify_ssl: bool = False


class TautulliServer(NamedTuple):
    api_key: str = None
    fallback_ip: str = None
    get_activity: bool = False
    get_activity_run_seconds: int = 30
    get_stats: bool = False
    get_stats_run_seconds: int = 30
    id: int = None
    url: str = None
    verify_ssl: bool = None


class SickChillServer(NamedTuple):
    api_key: str = None
    get_missing: bool = False
    get_missing_run_seconds: int = 30
    id: int = None
    url: str = None
    verify_ssl: bool = False


class CiscoASAFirewall(NamedTuple):
    get_bandwidth_run_seconds: int = 30
    id: int = None
    outside_interface: str = None
    password: str = 'cisco'
    url: str = '192.168.1.1'
    username: str = 'cisco'
    verify_ssl: bool = False


# Shared
class Queue(NamedTuple):
    downloadId: str = None
    episode: dict = None
    estimatedCompletionTime: str = None
    id: int = None
    movie: dict = None
    protocol: str = None
    quality: dict = None
    series: dict = None
    size: float = None
    sizeleft: float = None
    status: str = None
    statusMessages: list = None
    timeleft: str = None
    title: str = None
    trackedDownloadStatus: str = None


# Ombi Structures
class OmbiRequestCounts(NamedTuple):
    approved: int = 0
    available: int = 0
    pending: int = 0


class OmbiIssuesCounts(NamedTuple):
    inProgress: int = 0
    pending: int = 0
    resolved: int = 0


class OmbiTVRequest(NamedTuple):
    background: str = None
    childRequests: list = None
    denied: bool = None
    deniedReason: None = None
    id: int = None
    imdbId: str = None
    markedAsDenied: str = None
    overview: str = None
    posterPath: str = None
    qualityOverride: None = None
    releaseDate: str = None
    rootFolder: None = None
    status: str = None
    title: str = None
    totalSeasons: int = None
    tvDbId: int = None


class OmbiMovieRequest(NamedTuple):
    approved: bool = None
    available: bool = None
    background: str = None
    canApprove: bool = None
    denied: bool = None
    deniedReason: None = None
    digitalRelease: bool = None
    digitalReleaseDate: None = None
    id: int = None
    imdbId: str = None
    issueId: None = None
    issues: None = None
    markedAsApproved: str = None
    markedAsAvailable: None = None
    markedAsDenied: str = None
    overview: str = None
    posterPath: str = None
    qualityOverride: int = None
    released: bool = None
    releaseDate: str = None
    requestedDate: str = None
    requestedUser: dict = None
    requestedUserId: str = None
    requestType: int = None
    rootPathOverride: int = None
    showSubscribe: bool = None
    status: str = None
    subscribed: bool = None
    theMovieDbId: int = None
    title: str = None


# Sonarr
class TVShow(NamedTuple):
    absoluteEpisodeNumber: int = None
    airDate: str = None
    airDateUtc: str = None
    episodeFile: dict = None
    episodeFileId: int = None
    episodeNumber: int = None
    hasFile: bool = None
    id: int = None
    lastSearchTime: str = None
    monitored: bool = None
    overview: str = None
    sceneAbsoluteEpisodeNumber: int = None
    sceneEpisodeNumber: int = None
    sceneSeasonNumber: int = None
    seasonNumber: int = None
    series: dict = None
    seriesId: int = None
    title: str = None
    unverifiedSceneNumbering: bool = None


# Radarr
class Movie(NamedTuple):
    added: str = None
    addOptions: str = None
    alternativeTitles: list = None
    certification: str = None
    cleanTitle: str = None
    downloaded: bool = None
    folderName: str = None
    genres: list = None
    hasFile: bool = None
    id: int = None
    images: list = None
    imdbId: str = None
    inCinemas: str = None
    isAvailable: bool = None
    lastInfoSync: str = None
    minimumAvailability: str = None
    monitored: bool = None
    movieFile: dict = None
    overview: str = None
    path: str = None
    pathState: str = None
    physicalRelease: str = None
    physicalReleaseNote: str = None
    profileId: int = None
    qualityProfileId: int = None
    ratings: dict = None
    runtime: int = None
    secondaryYear: str = None
    secondaryYearSourceId: int = None
    sizeOnDisk: int = None
    sortTitle: str = None
    status: str = None
    studio: str = None
    tags: list = None
    title: str = None
    titleSlug: str = None
    tmdbId: int = None
    website: str = None
    year: int = None
    youTubeTrailerId: str = None


# Sickchill
class SickChillTVShow(NamedTuple):
    airdate: str = None
    airs: str = None
    episode: int = None
    ep_name: str = None
    ep_plot: str = None
    indexerid: int = None
    network: str = None
    paused: int = None
    quality: str = None
    season: int = None
    show_name: str = None
    show_status: str = None
    tvdbid: int = None
    weekday: int = None


# Tautulli
class TautulliStream(NamedTuple):
    actors: list = None
    added_at: str = None
    allow_guest: int = None
    art: str = None
    aspect_ratio: str = None
    audience_rating: str = None
    audience_rating_image: str = None
    audio_bitrate: str = None
    audio_bitrate_mode: str = None
    audio_channels: str = None
    audio_channel_layout: str = None
    audio_codec: str = None
    audio_decision: str = None
    audio_language: str = None
    audio_language_code: str = None
    audio_profile: str = None
    audio_sample_rate: str = None
    bandwidth: str = None
    banner: str = None
    bif_thumb: str = None
    bitrate: str = None
    channel_icon: str = None
    channel_stream: int = None
    channel_title: str = None
    children_count: str = None
    collections: list = None
    container: str = None
    content_rating: str = None
    deleted_user: int = None
    device: str = None
    directors: list = None
    do_notify: int = None
    duration: str = None
    email: str = None
    extra_type: str = None
    file: str = None
    file_size: str = None
    friendly_name: str = None
    full_title: str = None
    genres: list = None
    grandparent_rating_key: str = None
    grandparent_thumb: str = None
    grandparent_title: str = None
    guid: str = None
    height: str = None
    id: str = None
    indexes: int = None
    ip_address: str = None
    ip_address_public: str = None
    is_admin: int = None
    is_allow_sync: int = None
    is_home_user: int = None
    is_restricted: int = None
    keep_history: int = None
    labels: list = None
    last_viewed_at: str = None
    library_name: str = None
    live: int = None
    live_uuid: str = None
    local: str = None
    location: str = None
    machine_id: str = None
    media_index: str = None
    media_type: str = None
    optimized_version: int = None
    optimized_version_profile: str = None
    optimized_version_title: str = None
    originally_available_at: str = None
    original_title: str = None
    parent_media_index: str = None
    parent_rating_key: str = None
    parent_thumb: str = None
    parent_title: str = None
    platform: str = None
    platform_name: str = None
    platform_version: str = None
    player: str = None
    product: str = None
    product_version: str = None
    profile: str = None
    progress_percent: str = None
    quality_profile: str = None
    rating: str = None
    rating_image: str = None
    rating_key: str = None
    relay: int = None
    section_id: str = None
    selected: int = None
    session_id: str = None
    session_key: str = None
    shared_libraries: list = None
    sort_title: str = None
    state: str = None
    stream_aspect_ratio: str = None
    stream_audio_bitrate: str = None
    stream_audio_bitrate_mode: str = None
    stream_audio_channels: str = None
    stream_audio_channel_layout: str = None
    stream_audio_channel_layout_: str = None
    stream_audio_codec: str = None
    stream_audio_decision: str = None
    stream_audio_language: str = None
    stream_audio_language_code: str = None
    stream_audio_sample_rate: str = None
    stream_bitrate: str = None
    stream_container: str = None
    stream_container_decision: str = None
    stream_duration: str = None
    stream_subtitle_codec: str = None
    stream_subtitle_container: str = None
    stream_subtitle_decision: str = None
    stream_subtitle_forced: int = None
    stream_subtitle_format: str = None
    stream_subtitle_language: str = None
    stream_subtitle_language_code: str = None
    stream_subtitle_location: str = None
    stream_video_bitrate: str = None
    stream_video_bit_depth: str = None
    stream_video_codec: str = None
    stream_video_codec_level: str = None
    stream_video_decision: str = None
    stream_video_framerate: str = None
    stream_video_height: str = None
    stream_video_language: str = None
    stream_video_language_code: str = None
    stream_video_ref_frames: str = None
    stream_video_resolution: str = None
    stream_video_width: str = None
    studio: str = None
    subtitles: int = None
    subtitle_codec: str = None
    subtitle_container: str = None
    subtitle_decision: str = None
    subtitle_forced: int = None
    subtitle_format: str = None
    subtitle_language: str = None
    subtitle_language_code: str = None
    subtitle_location: str = None
    sub_type: str = None
    summary: str = None
    synced_version: int = None
    synced_version_profile: str = None
    tagline: str = None
    throttled: str = None
    thumb: str = None
    title: str = None
    transcode_audio_channels: str = None
    transcode_audio_codec: str = None
    transcode_container: str = None
    transcode_decision: str = None
    transcode_height: str = None
    transcode_hw_decode: str = None
    transcode_hw_decode_title: str = None
    transcode_hw_decoding: int = None
    transcode_hw_encode: str = None
    transcode_hw_encode_title: str = None
    transcode_hw_encoding: int = None
    transcode_hw_full_pipeline: int = None
    transcode_hw_requested: int = None
    transcode_key: str = None
    transcode_progress: int = None
    transcode_protocol: str = None
    transcode_speed: str = None
    transcode_throttled: int = None
    transcode_video_codec: str = None
    transcode_width: str = None
    type: str = None
    updated_at: str = None
    user: str = None
    username: str = None
    user_id: int = None
    user_rating: str = None
    user_thumb: str = None
    video_bitrate: str = None
    video_bit_depth: str = None
    video_codec: str = None
    video_codec_level: str = None
    video_decision: str = None
    video_framerate: str = None
    video_frame_rate: str = None
    video_height: str = None
    video_language: str = None
    video_language_code: str = None
    video_profile: str = None
    video_ref_frames: str = None
    video_resolution: str = None
    video_width: str = None
    view_offset: str = None
    width: str = None
    writers: list = None
    year: str = None
