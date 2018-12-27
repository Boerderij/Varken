from sys import version_info
from typing import NamedTuple
from logging import getLogger

logger = getLogger('temp')
# Check for python3.6 or newer to resolve erroneous typing.NamedTuple issues
if version_info < (3, 6):
    logger.error('Varken requires python3.6 or newer. You are on python%s.%s - Exiting...',
                 version_info.major, version_info.minor)
    exit(1)


class Queue(NamedTuple):
    movie: dict = None
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
    queue_run_seconds: int = 30


class RadarrServer(NamedTuple):
    id: int = None
    url: str = None
    api_key: str = None
    verify_ssl: bool = False
    queue: bool = False
    queue_run_seconds: int = 30
    get_missing: bool = False
    get_missing_run_seconds: int = 30


class OmbiServer(NamedTuple):
    id: int = None
    url: str = None
    api_key: str = None
    verify_ssl: bool = False
    request_type_counts: bool = False
    request_type_run_seconds: int = 30
    request_total_counts: bool = False
    request_total_run_seconds: int = 30
    issue_status_counts: bool = False
    issue_status_run_seconds: int = 30
    issue_total_counts: bool = False
    issue_total_run_seconds: int = 30


class TautulliServer(NamedTuple):
    id: int = None
    url: str = None
    fallback_ip: str = None
    api_key: str = None
    verify_ssl: bool = None
    get_activity: bool = False
    get_activity_run_seconds: int = 30
    get_stats: bool = False
    get_stats_run_seconds: int = 30


class InfluxServer(NamedTuple):
    url: str = 'localhost'
    port: int = 8086
    username: str = 'root'
    password: str = 'root'


class SickChillServer(NamedTuple):
    id: int = None
    url: str = None
    api_key: str = None
    verify_ssl: bool = False
    get_missing: bool = False
    get_missing_run_seconds: int = 30


class CiscoASAFirewall(NamedTuple):
    id: int = None
    url: str = '192.168.1.1'
    username: str = 'cisco'
    password: str = 'cisco'
    outside_interface: str = None
    verify_ssl: bool = False
    get_bandwidth_run_seconds: int = 30


class OmbiRequestCounts(NamedTuple):
    pending: int = 0
    approved: int = 0
    available: int = 0

class OmbiIssuesCounts(NamedTuple):
    pending: int = 0
    inProgress: int = 0
    resolved: int = 0


class TautulliStream(NamedTuple):
    rating: str = None
    transcode_width: str = None
    labels: list = None
    stream_bitrate: str = None
    bandwidth: str = None
    optimized_version: int = None
    video_language: str = None
    parent_rating_key: str = None
    rating_key: str = None
    platform_version: str = None
    transcode_hw_decoding: int = None
    thumb: str = None
    title: str = None
    video_codec_level: str = None
    tagline: str = None
    last_viewed_at: str = None
    audio_sample_rate: str = None
    user_rating: str = None
    platform: str = None
    collections: list = None
    location: str = None
    transcode_container: str = None
    audio_channel_layout: str = None
    local: str = None
    stream_subtitle_format: str = None
    stream_video_ref_frames: str = None
    transcode_hw_encode_title: str = None
    stream_container_decision: str = None
    audience_rating: str = None
    full_title: str = None
    ip_address: str = None
    subtitles: int = None
    stream_subtitle_language: str = None
    channel_stream: int = None
    channel_icon: str = None
    channel_title: str = None
    video_bitrate: str = None
    is_allow_sync: int = None
    stream_video_bitrate: str = None
    summary: str = None
    stream_audio_decision: str = None
    aspect_ratio: str = None
    audio_bitrate_mode: str = None
    transcode_hw_decode_title: str = None
    stream_audio_channel_layout: str = None
    deleted_user: int = None
    library_name: str = None
    art: str = None
    stream_video_resolution: str = None
    video_profile: str = None
    sort_title: str = None
    stream_video_codec_level: str = None
    stream_video_height: str = None
    year: str = None
    stream_duration: str = None
    stream_audio_channels: str = None
    video_language_code: str = None
    transcode_key: str = None
    transcode_throttled: int = None
    container: str = None
    stream_audio_bitrate: str = None
    user: str = None
    selected: int = None
    product_version: str = None
    subtitle_location: str = None
    transcode_hw_requested: int = None
    video_height: str = None
    state: str = None
    is_restricted: int = None
    email: str = None
    stream_container: str = None
    transcode_speed: str = None
    video_bit_depth: str = None
    stream_audio_sample_rate: str = None
    grandparent_title: str = None
    studio: str = None
    transcode_decision: str = None
    video_width: str = None
    bitrate: str = None
    machine_id: str = None
    originally_available_at: str = None
    video_frame_rate: str = None
    synced_version_profile: str = None
    friendly_name: str = None
    audio_profile: str = None
    optimized_version_title: str = None
    platform_name: str = None
    stream_video_language: str = None
    keep_history: int = None
    stream_audio_codec: str = None
    stream_video_codec: str = None
    grandparent_thumb: str = None
    synced_version: int = None
    transcode_hw_decode: str = None
    user_thumb: str = None
    stream_video_width: str = None
    height: str = None
    stream_subtitle_decision: str = None
    audio_codec: str = None
    parent_title: str = None
    guid: str = None
    audio_language_code: str = None
    transcode_video_codec: str = None
    transcode_audio_codec: str = None
    stream_video_decision: str = None
    user_id: int = None
    transcode_height: str = None
    transcode_hw_full_pipeline: int = None
    throttled: str = None
    quality_profile: str = None
    width: str = None
    live: int = None
    stream_subtitle_forced: int = None
    media_type: str = None
    video_resolution: str = None
    stream_subtitle_location: str = None
    do_notify: int = None
    video_ref_frames: str = None
    stream_subtitle_language_code: str = None
    audio_channels: str = None
    stream_audio_language_code: str = None
    optimized_version_profile: str = None
    relay: int = None
    duration: str = None
    rating_image: str = None
    is_home_user: int = None
    is_admin: int = None
    ip_address_public: str = None
    allow_guest: int = None
    transcode_audio_channels: str = None
    stream_audio_channel_layout_: str = None
    media_index: str = None
    stream_video_framerate: str = None
    transcode_hw_encode: str = None
    grandparent_rating_key: str = None
    original_title: str = None
    added_at: str = None
    banner: str = None
    bif_thumb: str = None
    parent_media_index: str = None
    live_uuid: str = None
    audio_language: str = None
    stream_audio_bitrate_mode: str = None
    username: str = None
    subtitle_decision: str = None
    children_count: str = None
    updated_at: str = None
    player: str = None
    subtitle_format: str = None
    file: str = None
    file_size: str = None
    session_key: str = None
    id: str = None
    subtitle_container: str = None
    genres: list = None
    stream_video_language_code: str = None
    indexes: int = None
    video_decision: str = None
    stream_audio_language: str = None
    writers: list = None
    actors: list = None
    progress_percent: str = None
    audio_decision: str = None
    subtitle_forced: int = None
    profile: str = None
    product: str = None
    view_offset: str = None
    type: str = None
    audience_rating_image: str = None
    audio_bitrate: str = None
    section_id: str = None
    stream_subtitle_codec: str = None
    subtitle_codec: str = None
    video_codec: str = None
    device: str = None
    stream_video_bit_depth: str = None
    video_framerate: str = None
    transcode_hw_encoding: int = None
    transcode_protocol: str = None
    shared_libraries: list = None
    stream_aspect_ratio: str = None
    content_rating: str = None
    session_id: str = None
    directors: list = None
    parent_thumb: str = None
    subtitle_language_code: str = None
    transcode_progress: int = None
    subtitle_language: str = None
    stream_subtitle_container: str = None
    sub_type: str = None
    extra_type: str = None


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
    sceneAbsoluteEpisodeNumber: int = None
    sceneEpisodeNumber: int = None
    sceneSeasonNumber: int = None
    series: dict = None
    id: int = None


class Movie(NamedTuple):
    title: str = None
    alternativeTitles: list = None
    secondaryYearSourceId: int = None
    sortTitle: str = None
    sizeOnDisk: int = None
    status: str = None
    overview: str = None
    inCinemas: str = None
    images: list = None
    downloaded: bool = None
    year: int = None
    secondaryYear: str = None
    hasFile: bool = None
    youTubeTrailerId: str = None
    studio: str = None
    path: str = None
    profileId: int = None
    pathState: str = None
    monitored: bool = None
    minimumAvailability: str = None
    isAvailable: bool = None
    folderName: str = None
    runtime: int = None
    lastInfoSync: str = None
    cleanTitle: str = None
    imdbId: str = None
    tmdbId: int = None
    titleSlug: str = None
    genres: list = None
    tags: list = None
    added: str = None
    ratings: dict = None
    movieFile: dict = None
    qualityProfileId: int = None
    physicalRelease: str = None
    physicalReleaseNote: str = None
    website: str = None
    id: int = None


class OmbiMovieRequest(NamedTuple):
    theMovieDbId: int = None
    issueId: None = None
    issues: None = None
    subscribed: bool = None
    showSubscribe: bool = None
    rootPathOverride: int = None
    qualityOverride: int = None
    imdbId: str = None
    overview: str = None
    posterPath: str = None
    releaseDate: str = None
    digitalReleaseDate: None = None
    status: str = None
    background: str = None
    released: bool = None
    digitalRelease: bool = None
    title: str = None
    approved: bool = None
    markedAsApproved: str = None
    requestedDate: str = None
    available: bool = None
    markedAsAvailable: None = None
    requestedUserId: str = None
    denied: bool = None
    markedAsDenied: str = None
    deniedReason: None = None
    requestType: int = None
    requestedUser: dict = None
    canApprove: bool = None
    id: int = None

class OmbiIssue(NamedTuple):
    title: str = None
    requestType:  int = None
    providerId: int = None
    requestId: int = None
    subject: str = None
    description: str = None
    issueCategoryId: int = None
    issueCategory: dict = None
    status: int = None
    resovledDate: None = None
    userReportedId: str = None
    userReported: str = None
    comments: str = None
    id: int = None


class OmbiTVRequest(NamedTuple):
    tvDbId: int = None
    imdbId: str = None
    qualityOverride: None = None
    rootFolder: None = None
    overview: str = None
    title: str = None
    posterPath: str = None
    background: str = None
    releaseDate: str = None
    status: str = None
    totalSeasons: int = None
    childRequests: list = None
    id: int = None
    denied: bool = None
    markedAsDenied: str = None
    deniedReason: None = None


class SickChillTVShow(NamedTuple):
    airdate: str = None
    airs: str = None
    ep_name: str = None
    ep_plot: str = None
    episode: int = None
    indexerid: int = None
    network: str = None
    paused: int = None
    quality: str = None
    season: int = None
    show_name: str = None
    show_status: str = None
    tvdbid: int = None
    weekday: int = None
