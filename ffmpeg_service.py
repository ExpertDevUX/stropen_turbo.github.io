import subprocess
import threading
import logging
import os
import json
from datetime import datetime
from config import VIDEO_PRESETS, QUALITY_PROFILES, HLS_SETTINGS, DASH_SETTINGS, FFMPEG_PATH

logger = logging.getLogger(__name__)

class FFmpegService:
    def __init__(self):
        self.active_streams = {}
        self.processes = {}
    
    def start_stream(self, stream_id, input_url, output_configs):
        """Start FFmpeg process for a stream with multiple outputs"""
        if stream_id in self.active_streams:
            logger.warning(f"Stream {stream_id} is already running")
            return False
        
        try:
            # Build FFmpeg command
            cmd = self._build_ffmpeg_command(input_url, output_configs)
            logger.info(f"Starting stream {stream_id} with command: {' '.join(cmd)}")
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            self.processes[stream_id] = process
            self.active_streams[stream_id] = {
                'process': process,
                'start_time': datetime.utcnow(),
                'input_url': input_url,
                'output_configs': output_configs
            }
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_stream,
                args=(stream_id, process)
            )
            monitor_thread.daemon = True
            monitor_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting stream {stream_id}: {e}")
            return False
    
    def stop_stream(self, stream_id):
        """Stop FFmpeg process for a stream"""
        if stream_id not in self.active_streams:
            logger.warning(f"Stream {stream_id} is not running")
            return False
        
        try:
            process = self.processes[stream_id]
            process.terminate()
            process.wait(timeout=10)
            
            del self.active_streams[stream_id]
            del self.processes[stream_id]
            
            logger.info(f"Stream {stream_id} stopped")
            return True
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Force killing stream {stream_id}")
            if stream_id in self.processes:
                process = self.processes[stream_id]
                process.kill()
            return True
        except Exception as e:
            logger.error(f"Error stopping stream {stream_id}: {e}")
            return False
    
    def _build_ffmpeg_command(self, input_url, output_configs):
        """Build FFmpeg command with multiple outputs"""
        cmd = [FFMPEG_PATH, '-i', input_url]
        
        # Add global options
        cmd.extend([
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-f', 'tee'
        ])
        
        # Build tee output string for multiple destinations
        outputs = []
        
        for config in output_configs:
            if config['type'] == 'hls':
                outputs.append(self._build_hls_output(config))
            elif config['type'] == 'dash':
                outputs.append(self._build_dash_output(config))
            elif config['type'] == 'rtmp':
                outputs.append(self._build_rtmp_output(config))
        
        if outputs:
            cmd.append('|'.join(outputs))
        
        return cmd
    
    def _build_hls_output(self, config):
        """Build HLS output configuration"""
        latency_mode = config.get('latency_mode', 'low_latency')
        settings = HLS_SETTINGS[latency_mode]
        
        output = f"[select=v:0,a:0:f=hls"
        output += f":hls_time={settings['segment_time']}"
        output += f":hls_list_size={settings['playlist_size']}"
        output += f":hls_flags={settings['flags']}"
        
        # Add quality-specific settings
        if 'resolution' in config:
            quality = QUALITY_PROFILES[config['resolution']]
            output += f":s={quality['width']}x{quality['height']}"
            output += f":b:v={quality['bitrate']}k"
        
        output += f"]{config['output_path']}"
        return output
    
    def _build_dash_output(self, config):
        """Build DASH output configuration"""
        latency_mode = config.get('latency_mode', 'low_latency')
        settings = DASH_SETTINGS[latency_mode]
        
        output = f"[select=v:0,a:0:f=dash"
        output += f":seg_duration={settings['segment_duration']}"
        output += f":window_size={settings['window_size']}"
        
        if settings['ldash']:
            output += ":ldash=1"
        
        # Add quality-specific settings
        if 'resolution' in config:
            quality = QUALITY_PROFILES[config['resolution']]
            output += f":s={quality['width']}x{quality['height']}"
            output += f":b:v={quality['bitrate']}k"
        
        output += f"]{config['output_path']}"
        return output
    
    def _build_rtmp_output(self, config):
        """Build RTMP output configuration"""
        output = f"[select=v:0,a:0:f=flv"
        
        # Add quality-specific settings
        if 'resolution' in config:
            quality = QUALITY_PROFILES[config['resolution']]
            output += f":s={quality['width']}x{quality['height']}"
            output += f":b:v={quality['bitrate']}k"
        
        output += f"]{config['rtmp_url']}/{config['stream_key']}"
        return output
    
    def _monitor_stream(self, stream_id, process):
        """Monitor FFmpeg process and log output"""
        try:
            for line in process.stderr:
                if line.strip():
                    logger.debug(f"Stream {stream_id}: {line.strip()}")
                    
                    # Parse FFmpeg output for statistics
                    self._parse_ffmpeg_stats(stream_id, line)
            
        except Exception as e:
            logger.error(f"Error monitoring stream {stream_id}: {e}")
        finally:
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
    
    def _parse_ffmpeg_stats(self, stream_id, line):
        """Parse FFmpeg output for stream statistics"""
        # This would parse FFmpeg output to extract bitrate, fps, etc.
        # Implementation would depend on specific FFmpeg output format
        pass
    
    def get_stream_status(self, stream_id):
        """Get current status of a stream"""
        if stream_id not in self.active_streams:
            return {'status': 'stopped'}
        
        stream_info = self.active_streams[stream_id]
        process = stream_info['process']
        
        if process.poll() is None:
            return {
                'status': 'running',
                'start_time': stream_info['start_time'],
                'uptime': (datetime.utcnow() - stream_info['start_time']).total_seconds()
            }
        else:
            return {'status': 'error', 'return_code': process.returncode}
    
    def list_active_streams(self):
        """List all active streams"""
        return list(self.active_streams.keys())

# Global FFmpeg service instance
ffmpeg_service = FFmpegService()
