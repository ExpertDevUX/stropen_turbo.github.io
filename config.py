import os

# Video encoding presets
VIDEO_PRESETS = {
    'ultrafast': {'preset': 'ultrafast', 'crf': 28},
    'superfast': {'preset': 'superfast', 'crf': 26},
    'veryfast': {'preset': 'veryfast', 'crf': 24},
    'faster': {'preset': 'faster', 'crf': 23},
    'fast': {'preset': 'fast', 'crf': 22},
    'medium': {'preset': 'medium', 'crf': 21},
    'slow': {'preset': 'slow', 'crf': 20},
}

# Resolution and bitrate settings
QUALITY_PROFILES = {
    '240p': {'width': 426, 'height': 240, 'bitrate': 400},
    '360p': {'width': 640, 'height': 360, 'bitrate': 700},
    '480p': {'width': 854, 'height': 480, 'bitrate': 1200},
    '720p': {'width': 1280, 'height': 720, 'bitrate': 2500},
    '1080p': {'width': 1920, 'height': 1080, 'bitrate': 5000},
}

# HLS settings for different latency modes
HLS_SETTINGS = {
    'low_latency': {
        'segment_time': 1,
        'playlist_size': 3,
        'flags': '+delete_segments+program_date_time'
    },
    'tutorial': {
        'segment_time': 3,
        'playlist_size': 4,
        'flags': '+delete_segments+program_date_time'
    },
    'high_quality': {
        'segment_time': 6,
        'playlist_size': 5,
        'flags': '+delete_segments'
    }
}

# DASH settings
DASH_SETTINGS = {
    'low_latency': {
        'segment_duration': 1,
        'window_size': 3,
        'ldash': True
    },
    'tutorial': {
        'segment_duration': 2,
        'window_size': 4,
        'ldash': True
    },
    'high_quality': {
        'segment_duration': 4,
        'window_size': 5,
        'ldash': False
    }
}

# Platform-specific RTMP endpoints
PLATFORM_ENDPOINTS = {
    'tutorial': 'rtmp://tutorial-platform.com/live/',
    'youtube': 'rtmp://a.rtmp.youtube.com/live2/',
    'twitch': 'rtmp://live.twitch.tv/live/',
    'facebook': 'rtmps://live-api-s.facebook.com:443/rtmp/',
    'instagram': 'rtmps://live-upload.instagram.com:443/rtmp/',
}

# FFmpeg paths
FFMPEG_PATH = os.environ.get('FFMPEG_PATH', 'ffmpeg')
FFPROBE_PATH = os.environ.get('FFPROBE_PATH', 'ffprobe')
