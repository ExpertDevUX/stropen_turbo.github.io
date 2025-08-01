import threading
import subprocess
import logging
import os
import signal
from datetime import datetime
from models import Stream, db
from stream_manager import stream_manager

logger = logging.getLogger(__name__)

class RTMPServer:
    def __init__(self, port=1935):
        self.port = port
        self.server_process = None
        self.is_running = False
        self.streams = {}
        
    def start_server(self):
        """Start the RTMP server using FFmpeg"""
        if self.is_running:
            logger.warning("RTMP server is already running")
            return True
            
        try:
            # Create RTMP server using FFmpeg (simple implementation)
            # In production, you'd use nginx-rtmp-module or similar
            self.is_running = True
            logger.info(f"RTMP server started on port {self.port}")
            
            # Start monitoring thread for incoming streams
            monitor_thread = threading.Thread(target=self._monitor_incoming_streams)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start RTMP server: {e}")
            return False
    
    def stop_server(self):
        """Stop the RTMP server"""
        try:
            if self.server_process:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            
            self.is_running = False
            logger.info("RTMP server stopped")
            return True
            
        except subprocess.TimeoutExpired:
            if self.server_process:
                self.server_process.kill()
            return True
        except Exception as e:
            logger.error(f"Error stopping RTMP server: {e}")
            return False
    
    def _monitor_incoming_streams(self):
        """Monitor for incoming RTMP streams"""
        # This is a simplified implementation
        # In production, you'd integrate with nginx-rtmp-module callbacks
        while self.is_running:
            try:
                # Check for new streams every 5 seconds
                threading.Event().wait(5)
                # Implementation would monitor RTMP connections
                
            except Exception as e:
                logger.error(f"Error monitoring RTMP streams: {e}")
    
    def handle_stream_publish(self, stream_key, client_ip=None):
        """Handle new stream publication"""
        try:
            # Check if stream already exists
            stream = Stream.query.filter_by(input_url=f"rtmp://localhost:{self.port}/live/{stream_key}").first()
            
            if not stream:
                # Auto-create stream for new stream key
                stream = Stream(
                    name=f"RTMP Stream - {stream_key}",
                    input_url=f"rtmp://localhost:{self.port}/live/{stream_key}",
                    input_type="rtmp",
                    status="running",
                    latency_mode="low",
                    record_enabled=False,
                    video_codec="h264",
                    audio_codec="aac",
                    bitrate_mode="cbr",
                    keyframe_interval=2
                )
                
                db.session.add(stream)
                db.session.commit()
                
                # Create default outputs
                stream_manager._create_default_outputs(stream.id, ['720p'])
                
                logger.info(f"Auto-created stream {stream.id} for key {stream_key}")
            
            # Start processing the stream
            self.streams[stream_key] = {
                'stream_id': stream.id,
                'start_time': datetime.utcnow(),
                'client_ip': client_ip
            }
            
            # Start stream processing
            stream_manager.start_stream(stream.id)
            
            return stream.id
            
        except Exception as e:
            logger.error(f"Error handling stream publish for key {stream_key}: {e}")
            return None
    
    def handle_stream_unpublish(self, stream_key):
        """Handle stream unpublication"""
        try:
            if stream_key in self.streams:
                stream_info = self.streams[stream_key]
                stream_id = stream_info['stream_id']
                
                # Stop stream processing
                stream_manager.stop_stream(stream_id)
                
                # Update stream status
                stream = Stream.query.get(stream_id)
                if stream:
                    stream.status = 'stopped'
                    db.session.commit()
                
                del self.streams[stream_key]
                logger.info(f"Stream {stream_key} unpublished")
                
        except Exception as e:
            logger.error(f"Error handling stream unpublish for key {stream_key}: {e}")
    
    def get_active_streams(self):
        """Get list of active RTMP streams"""
        return list(self.streams.keys())
    
    def get_server_status(self):
        """Get RTMP server status"""
        return {
            'running': self.is_running,
            'port': self.port,
            'active_streams': len(self.streams),
            'streams': self.streams
        }

# Global RTMP server instance
rtmp_server = RTMPServer()