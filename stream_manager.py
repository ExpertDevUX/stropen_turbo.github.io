import logging
import json
from datetime import datetime
from models import Stream, StreamOutput, StreamStats, StreamDestination, db
from ffmpeg_service import ffmpeg_service
from config import QUALITY_PROFILES, PLATFORM_ENDPOINTS
from app import app

logger = logging.getLogger(__name__)

class StreamManager:
    def __init__(self):
        self.streams = {}
    
    def create_stream(self, name, input_url, input_type, **kwargs):
        """Create a new stream configuration"""
        try:
            stream = Stream(
                name=name,
                input_url=input_url,
                input_type=input_type,
                latency_mode=kwargs.get('latency_mode', 'low'),
                record_enabled=kwargs.get('record_enabled', False),
                video_codec=kwargs.get('video_codec', 'h264'),
                audio_codec=kwargs.get('audio_codec', 'aac'),
                bitrate_mode=kwargs.get('bitrate_mode', 'cbr'),
                keyframe_interval=kwargs.get('keyframe_interval', 2)
            )
            
            db.session.add(stream)
            db.session.commit()
            
            # Create default output configurations
            self._create_default_outputs(stream.id, kwargs.get('qualities', ['720p']))
            
            logger.info(f"Created stream {stream.id}: {name}")
            return stream
            
        except Exception as e:
            logger.error(f"Error creating stream: {e}")
            db.session.rollback()
            return None
    
    def start_stream(self, stream_id):
        """Start streaming for a specific stream"""
        try:
            stream = Stream.query.get(stream_id)
            if not stream:
                logger.error(f"Stream {stream_id} not found")
                return False
            
            if stream.status == 'running':
                logger.warning(f"Stream {stream_id} is already running")
                return True
            
            # Build output configurations
            output_configs = self._build_output_configs(stream)
            
            # Start FFmpeg process
            success = ffmpeg_service.start_stream(
                stream_id,
                stream.input_url,
                output_configs
            )
            
            if success:
                stream.status = 'running'
                stream.updated_at = datetime.utcnow()
                db.session.commit()
                
                # Start statistics collection
                self._start_stats_collection(stream_id)
                
                logger.info(f"Started stream {stream_id}")
                return True
            else:
                stream.status = 'error'
                db.session.commit()
                return False
                
        except Exception as e:
            logger.error(f"Error starting stream {stream_id}: {e}")
            return False
    
    def stop_stream(self, stream_id):
        """Stop streaming for a specific stream"""
        try:
            stream = Stream.query.get(stream_id)
            if not stream:
                logger.error(f"Stream {stream_id} not found")
                return False
            
            # Stop FFmpeg process
            success = ffmpeg_service.stop_stream(stream_id)
            
            if success:
                stream.status = 'stopped'
                stream.updated_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Stopped stream {stream_id}")
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error stopping stream {stream_id}: {e}")
            return False
    
    def update_stream_destinations(self, stream_id, destinations):
        """Update RTMP destinations for a stream"""
        try:
            stream = Stream.query.get(stream_id)
            if not stream:
                return False
            
            stream.set_destinations(destinations)
            db.session.commit()
            
            # If stream is running, restart with new destinations
            if stream.status == 'running':
                self.stop_stream(stream_id)
                self.start_stream(stream_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating destinations for stream {stream_id}: {e}")
            return False
    
    def _create_default_outputs(self, stream_id, qualities):
        """Create default HLS and DASH outputs for stream"""
        try:
            for quality in qualities:
                if quality not in QUALITY_PROFILES:
                    continue
                
                # Create HLS output
                hls_output = StreamOutput(
                    stream_id=stream_id,
                    format_type='hls',
                    resolution=quality,
                    bitrate=QUALITY_PROFILES[quality]['bitrate'],
                    output_path=f"{app.config['HLS_OUTPUT_DIR']}/stream_{stream_id}_{quality}.m3u8"
                )
                db.session.add(hls_output)
                
                # Create DASH output
                dash_output = StreamOutput(
                    stream_id=stream_id,
                    format_type='dash',
                    resolution=quality,
                    bitrate=QUALITY_PROFILES[quality]['bitrate'],
                    output_path=f"{app.config['DASH_OUTPUT_DIR']}/stream_{stream_id}_{quality}.mpd"
                )
                db.session.add(dash_output)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error creating default outputs: {e}")
            db.session.rollback()
    
    def _build_output_configs(self, stream):
        """Build FFmpeg output configurations for a stream"""
        configs = []
        
        # Get stream outputs
        outputs = StreamOutput.query.filter_by(stream_id=stream.id).all()
        
        for output in outputs:
            config = {
                'type': output.format_type,
                'resolution': output.resolution,
                'output_path': output.output_path,
                'latency_mode': stream.latency_mode
            }
            configs.append(config)
        
        # Add RTMP destinations
        destinations = stream.get_destinations()
        for dest in destinations:
            if dest.get('enabled', True):
                config = {
                    'type': 'rtmp',
                    'rtmp_url': dest['rtmp_url'],
                    'stream_key': dest['stream_key'],
                    'resolution': dest.get('quality', '720p')
                }
                configs.append(config)
        
        return configs
    
    def _start_stats_collection(self, stream_id):
        """Start collecting statistics for a stream"""
        # This would start a background task to collect stream statistics
        # Implementation would depend on how stats are collected from FFmpeg
        pass
    
    def get_stream_stats(self, stream_id, limit=100):
        """Get recent statistics for a stream"""
        try:
            stats = StreamStats.query.filter_by(stream_id=stream_id)\
                .order_by(StreamStats.timestamp.desc())\
                .limit(limit).all()
            
            return [{
                'timestamp': stat.timestamp.isoformat(),
                'viewers': stat.viewers,
                'bitrate': stat.bitrate,
                'frame_rate': stat.frame_rate,
                'packet_loss': stat.packet_loss
            } for stat in stats]
            
        except Exception as e:
            logger.error(f"Error getting stats for stream {stream_id}: {e}")
            return []
    
    def get_embed_info(self, stream_id):
        """Get embed information for a stream"""
        try:
            stream = Stream.query.get(stream_id)
            if not stream:
                return None
            
            outputs = StreamOutput.query.filter_by(stream_id=stream_id).all()
            
            embed_info = {
                'stream_id': stream_id,
                'name': stream.name,
                'status': stream.status,
                'hls_urls': [],
                'dash_urls': []
            }
            
            for output in outputs:
                if output.format_type == 'hls':
                    embed_info['hls_urls'].append({
                        'quality': output.resolution,
                        'url': f"/static/streams/hls/stream_{stream_id}_{output.resolution}.m3u8"
                    })
                elif output.format_type == 'dash':
                    embed_info['dash_urls'].append({
                        'quality': output.resolution,
                        'url': f"/static/streams/dash/stream_{stream_id}_{output.resolution}.mpd"
                    })
            
            return embed_info
            
        except Exception as e:
            logger.error(f"Error getting embed info for stream {stream_id}: {e}")
            return None

# Global stream manager instance
stream_manager = StreamManager()
