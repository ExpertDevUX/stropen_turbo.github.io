from app import db
from datetime import datetime
from sqlalchemy import Text, JSON
import json

class Stream(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    input_url = db.Column(db.String(500), nullable=False)
    input_type = db.Column(db.String(20), nullable=False)  # rtmp, webrtc, srt
    status = db.Column(db.String(20), default='stopped')  # stopped, starting, running, error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Streaming settings
    latency_mode = db.Column(db.String(10), default='low')  # low, high
    record_enabled = db.Column(db.Boolean, default=False)
    
    # Video settings
    video_codec = db.Column(db.String(20), default='h264')
    audio_codec = db.Column(db.String(20), default='aac')
    bitrate_mode = db.Column(db.String(10), default='cbr')  # cbr, vbr
    keyframe_interval = db.Column(db.Integer, default=2)
    
    # Multi-destination settings
    destinations = db.Column(Text)  # JSON string of destinations
    
    def get_destinations(self):
        if self.destinations:
            return json.loads(self.destinations)
        return []
    
    def set_destinations(self, destinations_list):
        self.destinations = json.dumps(destinations_list)

class StreamOutput(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=False)
    format_type = db.Column(db.String(10), nullable=False)  # hls, dash
    resolution = db.Column(db.String(20), nullable=False)  # 720p, 1080p, etc
    bitrate = db.Column(db.Integer, nullable=False)
    output_path = db.Column(db.String(500), nullable=False)
    
    stream = db.relationship('Stream', backref=db.backref('outputs', lazy=True))

class StreamStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stream_id = db.Column(db.Integer, db.ForeignKey('stream.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    viewers = db.Column(db.Integer, default=0)
    bitrate = db.Column(db.Float, default=0.0)
    frame_rate = db.Column(db.Float, default=0.0)
    packet_loss = db.Column(db.Float, default=0.0)
    
    stream = db.relationship('Stream', backref=db.backref('stats', lazy=True))

class StreamDestination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # tutorial, youtube, twitch, facebook, custom
    rtmp_url = db.Column(db.String(500), nullable=False)
    stream_key = db.Column(db.String(200), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
