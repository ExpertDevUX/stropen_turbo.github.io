# Advanced Streaming Panel - Complete Tutorial

Welcome to the comprehensive tutorial for the Advanced Streaming Panel, a professional-grade live video streaming platform optimized for educational content and tutorial delivery.

## Table of Contents

1. [Quick Start Guide](#quick-start-guide)
2. [Installation Methods](#installation-methods)
3. [Basic Configuration](#basic-configuration)
4. [Creating Your First Stream](#creating-your-first-stream)
5. [Live Video Preview Setup](#live-video-preview-setup)
6. [Multi-Destination Streaming](#multi-destination-streaming)
7. [RTMP Server Configuration](#rtmp-server-configuration)
8. [Educational Content Optimization](#educational-content-optimization)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start Guide

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Streaming software (OBS Studio, Streamlabs, XSplit) - optional
- Basic understanding of video streaming concepts

### 5-Minute Setup
1. Run the automatic installer: `bash install.sh`
2. Access the dashboard at `http://localhost`
3. Create your first stream with Tutorial Mode
4. Start streaming and enjoy live video previews!

---

## Installation Methods

### Method 1: Automatic Installation (Recommended)

The easiest way to get started is using our automatic installation script:

```bash
# Download and run the installer
curl -fsSL https://raw.githubusercontent.com/your-repo/streaming-panel/main/install.sh | bash

# Or download first and inspect
wget https://raw.githubusercontent.com/your-repo/streaming-panel/main/install.sh
chmod +x install.sh
./install.sh
```

**What the installer does:**
- Installs all system dependencies (FFmpeg, PostgreSQL, Redis, Nginx)
- Sets up Python environment and dependencies
- Configures RTMP server with Nginx
- Creates database and admin user
- Sets up SSL certificates (optional)
- Configures system services

### Method 2: Manual Installation

For advanced users who want full control:

#### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip
sudo apt install -y ffmpeg postgresql nginx redis-server
sudo apt install -y libnginx-mod-rtmp supervisor
```

**CentOS/RHEL:**
```bash
sudo yum install -y python3.11 python3-pip
sudo yum install -y ffmpeg postgresql nginx redis
sudo yum install -y supervisor
```

**macOS:**
```bash
brew install python@3.11 ffmpeg postgresql nginx redis supervisor
brew install nginx-full --with-rtmp-module
```

#### Step 2: Setup Application

```bash
# Create project directory
sudo mkdir -p /opt/streaming-panel
sudo chown $USER:$USER /opt/streaming-panel
cd /opt/streaming-panel

# Clone repository
git clone https://github.com/your-repo/streaming-panel.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Step 3: Configure Database

```bash
# Create PostgreSQL user and database
sudo -u postgres createuser streamuser --pwprompt
sudo -u postgres createdb streamdb --owner=streamuser

# Initialize database
python3 -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### Step 4: Configure Environment

Create `.env` file:
```bash
DATABASE_URL=postgresql://streamuser:password@localhost/streamdb
SESSION_SECRET=your-secret-key-here
FFMPEG_PATH=/usr/bin/ffmpeg
REDIS_URL=redis://localhost:6379
```

### Method 3: Docker Installation

For containerized deployment:

```bash
# Clone repository
git clone https://github.com/your-repo/streaming-panel.git
cd streaming-panel

# Build and run with Docker Compose
docker-compose up -d
```

---

## Basic Configuration

### Dashboard Overview

The streaming panel dashboard provides:

1. **Stream Cards**: Live preview thumbnails with status indicators
2. **RTMP Server Controls**: Start/stop built-in RTMP server
3. **Statistics**: Real-time viewer counts and performance metrics
4. **Quick Actions**: Create streams, manage destinations

### First-Time Setup

1. **Access the Dashboard**
   - Open `http://localhost` in your browser
   - Login with admin credentials created during installation

2. **Configure RTMP Server**
   - Click "Start RTMP" to enable the built-in server
   - Note the RTMP URL: `rtmp://your-domain.com/live/`

3. **Set Default Preferences**
   - Navigate to Settings
   - Choose Tutorial Mode as default latency setting
   - Configure default video quality (720p recommended)

---

## Creating Your First Stream

### Using the Web Interface

1. **Create New Stream**
   ```
   Dashboard → New Stream → Basic Settings
   ```

2. **Configure Stream Settings**
   - **Name**: "My Tutorial Stream"
   - **Input Type**: RTMP
   - **Input URL**: `rtmp://localhost:1935/live/tutorial_stream`
   - **Latency Mode**: Tutorial Mode (3-5 seconds)
   - **Quality**: 720p, 480p, 360p

3. **Add Destinations**
   - Click "Add Platform"
   - Select "Tutorial" for educational content
   - Add YouTube, Twitch, or custom RTMP endpoints
   - Configure per-destination quality settings

4. **Advanced Settings**
   - **Video Codec**: H.264 (most compatible)
   - **Audio Codec**: AAC
   - **Bitrate Mode**: CBR for stable streaming
   - **Keyframe Interval**: 2 seconds

5. **Save and Start**
   - Click "Create Stream"
   - Return to dashboard and click "Start"

### Using RTMP Software

#### OBS Studio Setup

1. **Configure Stream Settings**
   ```
   Settings → Stream
   Service: Custom
   Server: rtmp://your-domain.com/live/
   Stream Key: tutorial_stream
   ```

2. **Video Settings**
   ```
   Settings → Video
   Base Resolution: 1920x1080
   Output Resolution: 1280x720
   FPS: 30
   ```

3. **Output Settings**
   ```
   Settings → Output
   Encoder: x264
   Bitrate: 2500 kbps
   Keyframe Interval: 2s
   Profile: Main
   ```

#### Streamlabs OBS Setup

1. **Add Stream Destination**
   ```
   Settings → Stream
   Platform: Custom RTMP
   RTMP URL: rtmp://your-domain.com/live/
   Stream Key: tutorial_stream
   ```

2. **Quality Settings**
   ```
   Video Bitrate: 2500 kbps
   Audio Bitrate: 160 kbps
   Resolution: 1280x720
   Frame Rate: 30 FPS
   ```

---

## Live Video Preview Setup

### Enabling Live Previews

The streaming panel automatically displays live video previews for active streams:

1. **Automatic Detection**
   - Live previews appear when streams are running
   - Uses HLS.js for low-latency playback
   - Shows "LIVE" indicator with pulsing animation

2. **Preview Features**
   - Real-time video thumbnails in dashboard
   - Hover effects and smooth transitions
   - Offline indicators when streams stop
   - Automatic quality switching

3. **Technical Details**
   - Uses HLS segments for preview playback
   - 3-second segment duration for tutorial mode
   - Automatic retry on connection loss
   - Memory-efficient video players

### Customizing Preview Behavior

Edit `static/js/dashboard.js` to customize:

```javascript
// Modify preview update interval
setInterval(() => {
    this.updateLivePreviews();
}, 30000); // Update every 30 seconds

// Customize preview quality
const hlsUrl = `/static/streams/hls/stream_${streamId}_480p.m3u8`;
```

---

## Multi-Destination Streaming

### Supported Platforms

1. **Tutorial Platform**
   - Optimized for educational content
   - Balanced latency and quality settings
   - Custom RTMP endpoint configuration

2. **YouTube Live**
   - RTMP URL: `rtmp://a.rtmp.youtube.com/live2/`
   - Requires YouTube stream key
   - Supports up to 1080p60

3. **Twitch**
   - RTMP URL: `rtmp://live.twitch.tv/live/`
   - Requires Twitch stream key
   - Maximum 1080p60, 6000 kbps

4. **Facebook Live**
   - RTMPS URL: `rtmps://live-api-s.facebook.com:443/rtmp/`
   - Requires Facebook stream key
   - Supports up to 1080p30

5. **Custom RTMP**
   - Any RTMP-compatible platform
   - Configure custom URL and stream key
   - Full quality control

### Configuration Examples

#### Tutorial + YouTube Streaming

```yaml
Stream Name: "Programming Tutorial"
Primary Destination:
  - Platform: Tutorial
  - Quality: 720p, 480p
  - Latency: Tutorial Mode

Secondary Destination:
  - Platform: YouTube
  - Quality: 1080p
  - Latency: High Quality
  - Stream Key: your-youtube-key
```

#### Multi-Platform Educational Stream

```yaml
Destinations:
  1. Tutorial Platform (720p, Tutorial Mode)
  2. YouTube (1080p, High Quality)
  3. Twitch (720p, Low Latency)
  4. Custom LMS (480p, Tutorial Mode)
```

### Quality Optimization by Platform

| Platform | Recommended Quality | Bitrate | Latency Mode |
|----------|-------------------|---------|--------------|
| Tutorial | 720p | 2500 kbps | Tutorial Mode |
| YouTube | 1080p | 4500 kbps | High Quality |
| Twitch | 720p | 2500 kbps | Low Latency |
| Facebook | 720p | 2000 kbps | Tutorial Mode |

---

## RTMP Server Configuration

### Built-in RTMP Server

The streaming panel includes a powerful built-in RTMP server:

#### Features
- Auto-stream creation when clients connect
- Real-time status monitoring
- Support for multiple concurrent streams
- Automatic HLS and DASH generation
- Authentication and access control

#### Configuration

**Nginx RTMP Module Configuration:**
```nginx
rtmp {
    server {
        listen 1935;
        chunk_size 4096;
        
        application live {
            live on;
            record off;
            
            # Authentication
            on_publish http://127.0.0.1:5000/rtmp/auth;
            on_publish_done http://127.0.0.1:5000/rtmp/done;
            
            # HLS Configuration
            hls on;
            hls_path /opt/streaming-panel/static/streams/hls;
            hls_fragment 3s;
            hls_playlist_length 60s;
            
            # DASH Configuration
            dash on;
            dash_path /opt/streaming-panel/static/streams/dash;
            dash_fragment 3s;
            dash_playlist_length 60s;
        }
    }
}
```

### External RTMP Servers

You can also use external RTMP servers:

#### Wowza Streaming Engine
```yaml
RTMP URL: rtmp://your-wowza-server.com/live/
Application: live
Stream Name: your_stream_name
```

#### Node Media Server
```javascript
const NodeMediaServer = require('node-media-server');

const config = {
  rtmp: {
    port: 1935,
    chunk_size: 60000,
    gop_cache: true,
    ping: 30,
    ping_timeout: 60
  }
};

const nms = new NodeMediaServer(config);
nms.run();
```

---

## Educational Content Optimization

### Tutorial Mode Settings

Tutorial Mode is specifically designed for educational content:

#### Optimized Parameters
- **Latency**: 3-5 seconds (balanced for interaction)
- **Segment Duration**: 3 seconds
- **Playlist Length**: 4 segments
- **Quality**: Multi-bitrate adaptive
- **Encoding**: Fast preset for real-time processing

#### Best Practices

1. **Screen Sharing Optimization**
   ```
   Resolution: 1280x720 (16:9)
   Frame Rate: 30 FPS
   Bitrate: 2500 kbps
   Content: Programming/Tutorial optimized
   ```

2. **Audio Settings**
   ```
   Codec: AAC
   Bitrate: 160 kbps
   Sample Rate: 48 kHz
   Channels: Stereo
   ```

3. **Interaction Features**
   - Low-latency chat integration
   - Real-time Q&A capabilities
   - Screen annotation support
   - Breakout room compatibility

### Content-Specific Configurations

#### Programming Tutorials
```yaml
Video Settings:
  Resolution: 1280x720
  Frame Rate: 30 FPS
  Bitrate: 2500 kbps
  Codec: H.264 Fast

Audio Settings:
  Codec: AAC
  Bitrate: 160 kbps
  Sample Rate: 48 kHz

Special Features:
  - Code highlighting
  - Screen recording
  - Multiple monitor support
```

#### Live Lectures
```yaml
Video Settings:
  Resolution: 1920x1080
  Frame Rate: 30 FPS
  Bitrate: 3500 kbps
  Codec: H.264 Medium

Audio Settings:
  Codec: AAC
  Bitrate: 192 kbps
  Noise Suppression: Enabled

Special Features:
  - Slide integration
  - Whiteboard support
  - Recording capability
```

#### Interactive Workshops
```yaml
Video Settings:
  Resolution: 1280x720
  Frame Rate: 30 FPS
  Bitrate: 2000 kbps
  Codec: H.264 Fast

Latency: Low (1-3 seconds)
Interactive Features:
  - Real-time polls
  - Breakout rooms
  - Screen sharing
  - Chat integration
```

---

## Advanced Features

### Real-Time Analytics

Monitor your streams with comprehensive analytics:

#### Built-in Metrics
- **Viewer Count**: Real-time concurrent viewers
- **Bitrate Monitoring**: Upload and output bitrates
- **Quality Metrics**: Frame rate, resolution, packet loss
- **Geographic Distribution**: Viewer locations
- **Engagement**: Watch time, interaction rates

#### API Integration
```python
# Get stream statistics
@app.route('/api/stream/<int:stream_id>/stats')
def get_stream_stats(stream_id):
    stats = StreamStats.query.filter_by(stream_id=stream_id).all()
    return jsonify([{
        'timestamp': stat.timestamp,
        'viewers': stat.viewers,
        'bitrate': stat.bitrate,
        'frame_rate': stat.frame_rate
    } for stat in stats])
```

### WebRTC Integration

Enable ultra-low latency streaming with WebRTC:

#### Setup WebRTC Publisher
```javascript
const pc = new RTCPeerConnection({
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
});

// Add local stream
navigator.mediaDevices.getUserMedia({ video: true, audio: true })
    .then(stream => {
        stream.getTracks().forEach(track => {
            pc.addTrack(track, stream);
        });
    });
```

#### WebRTC Configuration
```yaml
WebRTC Settings:
  Protocol: WebRTC
  Latency: < 1 second
  Quality: Adaptive
  Compatibility: Modern browsers
  Fallback: HLS/DASH
```

### API Documentation

#### Stream Management API

**Create Stream:**
```bash
curl -X POST http://localhost:5000/api/streams \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Stream",
    "input_url": "rtmp://localhost:1935/live/test",
    "latency_mode": "tutorial",
    "qualities": ["720p", "480p"]
  }'
```

**Start Stream:**
```bash
curl -X POST http://localhost:5000/api/streams/1/start
```

**Get Stream Status:**
```bash
curl http://localhost:5000/api/streams/1/status
```

#### RTMP Server API

**Get Server Status:**
```bash
curl http://localhost:5000/api/rtmp/status
```

**Start/Stop Server:**
```bash
curl -X POST http://localhost:5000/api/rtmp/start
curl -X POST http://localhost:5000/api/rtmp/stop
```

### Custom Integrations

#### Learning Management System Integration

```python
# LMS webhook integration
@app.route('/webhook/lms', methods=['POST'])
def lms_webhook():
    data = request.json
    
    if data['event'] == 'class_started':
        # Auto-start stream for scheduled class
        stream = Stream.query.filter_by(
            name=data['class_name']
        ).first()
        
        if stream:
            start_stream(stream.id)
            
    return jsonify({'status': 'success'})
```

#### Video Conferencing Integration

```javascript
// Zoom SDK integration
const zoomSdk = require('@zoom/videosdk');

// Join meeting and stream
async function streamZoomMeeting(meetingId, streamKey) {
    await zoomSdk.join({
        topic: meetingId,
        userName: 'Streaming Bot'
    });
    
    // Capture video stream
    const stream = await zoomSdk.getVideoStream();
    
    // Send to RTMP endpoint
    sendToRTMP(stream, streamKey);
}
```

---

## Troubleshooting

### Common Issues

#### 1. Stream Won't Start

**Symptoms:**
- Stream status shows "Error"
- No video preview appears
- FFmpeg process fails

**Solutions:**
```bash
# Check FFmpeg installation
ffmpeg -version

# Verify input URL accessibility
ffprobe rtmp://your-input-url

# Check system resources
top
df -h

# Review application logs
tail -f /opt/streaming-panel/logs/app.log
```

#### 2. High Latency

**Symptoms:**
- Delay > 10 seconds in tutorial mode
- Viewers report lag
- Chat interactions delayed

**Solutions:**
```yaml
# Optimize HLS settings
HLS Settings:
  segment_time: 1    # Reduce to 1 second
  playlist_size: 2   # Reduce playlist size
  
# Use low latency mode
Latency Mode: Low Latency

# Check network conditions
ping your-server.com
traceroute your-server.com
```

#### 3. Poor Video Quality

**Symptoms:**
- Pixelated video
- Frame drops
- Audio issues

**Solutions:**
```yaml
# Increase bitrate
Video Bitrate: 3500 kbps  # For 720p
Audio Bitrate: 192 kbps

# Use better encoding preset
Encoding Preset: Medium  # Instead of Fast

# Check CPU usage
Encoder: Hardware accelerated (if available)
```

#### 4. RTMP Connection Fails

**Symptoms:**
- OBS can't connect
- "Connection failed" errors
- RTMP server offline

**Solutions:**
```bash
# Check RTMP server status
sudo systemctl status nginx
sudo nginx -t

# Verify firewall settings
sudo ufw status
sudo firewall-cmd --list-ports

# Test RTMP endpoint
ffmpeg -re -i test.mp4 -c copy -f flv rtmp://localhost:1935/live/test
```

### Performance Optimization

#### System Requirements

**Minimum Requirements:**
- CPU: 4 cores, 2.5 GHz
- RAM: 8 GB
- Storage: 50 GB SSD
- Network: 10 Mbps upload

**Recommended Requirements:**
- CPU: 8 cores, 3.0 GHz
- RAM: 16 GB
- Storage: 200 GB NVMe SSD
- Network: 50 Mbps upload

#### Optimization Tips

1. **CPU Optimization**
   ```bash
   # Use hardware encoding
   ffmpeg -hwaccel cuda -i input.mp4 ...
   
   # Optimize thread usage
   ffmpeg -threads 4 -i input.mp4 ...
   ```

2. **Memory Optimization**
   ```bash
   # Configure buffer sizes
   echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
   echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf
   ```

3. **Network Optimization**
   ```bash
   # Optimize TCP settings
   echo 'net.ipv4.tcp_congestion_control = bbr' >> /etc/sysctl.conf
   ```

### Monitoring and Logging

#### Log Locations

```bash
# Application logs
tail -f /opt/streaming-panel/logs/app.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql-14-main.log

# System logs
journalctl -u streaming-panel -f
```

#### Health Check Endpoints

```bash
# Application health
curl http://localhost:5000/health

# Database connectivity
curl http://localhost:5000/health/db

# RTMP server status
curl http://localhost:5000/health/rtmp
```

---

## Support and Resources

### Documentation Links

- [API Reference](./API.md)
- [Installation Guide](./INSTALL.md)
- [Configuration Reference](./CONFIG.md)
- [Developer Guide](./DEVELOPMENT.md)

### Community Support

- **GitHub Issues**: Report bugs and feature requests
- **Discord Server**: Real-time community support
- **Documentation Wiki**: Community-maintained guides
- **Video Tutorials**: Step-by-step setup guides

### Professional Support

For enterprise deployments and professional support:

**Expert Dev UX Professional Services**
- Custom deployment and configuration
- Performance optimization and scaling
- Integration development
- Training and consultation

Contact: support@expertdevux.com

---

## Conclusion

This tutorial covers the complete setup and usage of the Advanced Streaming Panel. The platform is designed to provide professional-grade streaming capabilities with a focus on educational content delivery.

Key takeaways:
- Use the automatic installer for quick setup
- Configure Tutorial Mode for educational content
- Enable live video previews for better monitoring
- Optimize settings based on your content type
- Monitor performance and troubleshoot issues proactively

**Next Steps:**
1. Complete the installation process
2. Create your first tutorial stream
3. Configure multi-destination streaming
4. Explore advanced features and integrations
5. Join the community for ongoing support

Happy streaming!

---

*Copyright © 2025 Expert Dev UX. All rights reserved.*