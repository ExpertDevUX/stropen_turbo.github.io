# Advanced Streaming Panel

A comprehensive Python-based live video streaming platform with low/high latency modes, multi-destination streaming, and real-time video preview capabilities.

## 🎯 Features

### Core Streaming Capabilities
- **Multi-format output**: HLS and DASH streaming protocols
- **Low/High latency modes**: Optimized for both real-time interaction and quality
- **Live video previews**: Real-time thumbnails in dashboard with HLS.js integration
- **Cross-platform embedding**: Embeddable video player for any website
- **Quality controls**: Multiple resolution outputs (240p to 1080p) with adaptive bitrates

### RTMP Server Integration
- **Built-in RTMP server**: Direct streaming from OBS, Streamlabs, or any RTMP client
- **Auto-stream creation**: Automatic stream setup when users publish to RTMP endpoints
- **Real-time monitoring**: Server status, active streams, and connection details
- **Easy configuration**: Copy-paste RTMP URLs for immediate use

### Multi-Destination Broadcasting
- **Platform support**: YouTube, Twitch, Facebook, Instagram, and custom RTMP endpoints
- **Simultaneous streaming**: Stream to multiple platforms with different quality settings
- **Flexible configuration**: Per-destination quality and encoding settings
- **Tutorial mode**: Optimized settings for educational content delivery

### Advanced Dashboard
- **Real-time statistics**: Live viewer counts, bitrates, and performance metrics
- **Stream management**: Start, stop, and configure streams from web interface
- **Live previews**: Video thumbnails with "LIVE" indicators and offline status
- **Responsive design**: Mobile-friendly interface with Bootstrap dark theme

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- FFmpeg
- PostgreSQL (production) or SQLite (development)

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   ```bash
   export DATABASE_URL="your_database_url"
   export SESSION_SECRET="your_secret_key"
   ```
4. Start the application:
   ```bash
   gunicorn --bind 0.0.0.0:5000 main:app
   ```

### RTMP Streaming Setup
1. Start the RTMP server from the dashboard
2. Configure your streaming software:
   - **Server URL**: `rtmp://your-domain.com/live/`
   - **Stream Key**: Use any unique identifier
3. Start streaming - the system will auto-create the stream

### Web Streaming Setup
1. Create a new stream in the dashboard
2. Configure destinations and quality settings
3. Use the provided RTMP endpoint or start streaming via web interface
4. Monitor live preview and statistics in real-time

## 🏗️ Architecture

### Backend Components
- **Flask Web Application**: RESTful API and web interface
- **SQLAlchemy ORM**: Database management with PostgreSQL/SQLite support
- **FFmpeg Service**: Video encoding and transcoding engine
- **RTMP Server**: Custom RTMP ingestion server
- **Stream Manager**: Orchestrates encoding processes and output management

### Frontend Components
- **Bootstrap UI**: Responsive dark theme interface
- **Video.js Player**: HTML5 video player with HLS/DASH support
- **HLS.js Integration**: Low-latency live preview functionality
- **Chart.js Analytics**: Real-time statistics and performance monitoring

### Streaming Pipeline
1. **Input Sources**: RTMP, SRT, WebRTC, or local media files
2. **Processing**: FFmpeg transcoding with configurable presets
3. **Output Formats**: HLS segments and DASH manifests
4. **Distribution**: Multi-destination broadcasting with quality variants
5. **Monitoring**: Real-time statistics and health checks

## 📊 Configuration Options

### Encoding Presets
- **Ultra Fast**: Minimal CPU usage, basic quality
- **Fast**: Balanced performance and quality
- **Medium**: Standard quality encoding
- **Slow**: High quality, increased CPU usage
- **Veryslow**: Maximum quality, highest CPU usage

### Latency Modes
- **Low Latency**: 1-3 second delay, optimized for real-time interaction
- **High Quality**: 10-30 second delay, optimized for video quality
- **Tutorial**: Balanced settings for educational content

### Quality Profiles
- **240p**: 400 kbps, mobile-optimized
- **360p**: 800 kbps, low bandwidth
- **480p**: 1200 kbps, standard definition
- **720p**: 2500 kbps, high definition
- **1080p**: 4500 kbps, full high definition

## 🔧 API Reference

### Stream Management
- `POST /stream/create` - Create new stream
- `GET /stream/{id}/status` - Get stream status
- `POST /stream/{id}/start` - Start streaming
- `POST /stream/{id}/stop` - Stop streaming
- `GET /stream/{id}/stats` - Get stream statistics

### RTMP Server
- `GET /rtmp/status` - Get server status
- `POST /rtmp/start` - Start RTMP server
- `POST /rtmp/stop` - Stop RTMP server

### Player Endpoints
- `GET /stream/{id}/player` - Standalone player page
- `GET /stream/{id}/embed` - Embeddable player
- `GET /static/streams/hls/{stream}.m3u8` - HLS manifest
- `GET /static/streams/dash/{stream}.mpd` - DASH manifest

## 🎨 User Experience Design

### Design Philosophy
The streaming panel follows modern UX principles with focus on:
- **Immediate feedback**: Real-time status updates and visual indicators
- **Progressive disclosure**: Advanced features accessible without cluttering basic interface
- **Mobile-first design**: Responsive layout adapting to all screen sizes
- **Accessibility**: WCAG compliant with keyboard navigation and screen reader support

### Visual Design System
- **Color Palette**: Bootstrap dark theme with custom accent colors
- **Typography**: Clear hierarchy with appropriate font weights and sizes
- **Iconography**: Font Awesome icons for consistent visual language
- **Animations**: Subtle transitions and loading states for smooth interactions

### Interaction Patterns
- **One-click actions**: Start/stop streaming with single button press
- **Drag and drop**: Easy file uploads and configuration
- **Copy-paste integration**: Quick access to stream URLs and embed codes
- **Real-time updates**: Live status changes without page refreshes

## 📄 License & Copyright

**Copyright © 2025 Expert Dev UX**

This streaming platform represents advanced software engineering practices combining:
- Modern web development frameworks (Flask, SQLAlchemy, Bootstrap)
- Professional video streaming technologies (FFmpeg, HLS, DASH)
- Enterprise-grade architecture patterns (microservices, real-time processing)
- Expert user experience design (responsive UI, accessibility, performance)

### Technical Excellence
The codebase demonstrates expertise in:
- **Backend Development**: RESTful APIs, database design, background processing
- **Frontend Engineering**: Modern JavaScript, responsive CSS, progressive enhancement
- **Video Technology**: Streaming protocols, encoding optimization, multi-format delivery
- **DevOps**: Container deployment, monitoring, scaling strategies

### Open Source Components
This project builds upon excellent open source technologies:
- Flask web framework and ecosystem
- FFmpeg video processing engine
- Video.js and HLS.js media players
- Bootstrap UI framework
- Chart.js data visualization

### Professional Usage
Suitable for:
- Corporate live streaming and webinars
- Educational platforms and e-learning
- Content creators and influencers
- Enterprise video communications
- Custom streaming applications

---

**Built with expertise in modern web development, video streaming technology, and user experience design.**

## 🚀 Quick Start

### Automatic Installation (Recommended)

Get started in minutes with our one-command installer:

```bash
curl -fsSL https://raw.githubusercontent.com/expertdevux/streaming-panel/main/install.sh | bash
```

Or download and review first:
```bash
wget https://github.com/expertdevux/streaming-panel/raw/main/install.sh
chmod +x install.sh
./install.sh
```

### Manual Installation

For advanced users who want full control:

```bash
# Clone repository
git clone https://github.com/expertdevux/streaming-panel.git
cd streaming-panel

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Initialize database
python manage.py db upgrade

# Start development server
python manage.py runserver
```

### Docker Deployment

```bash
# Clone and start with Docker
git clone https://github.com/expertdevux/streaming-panel.git
cd streaming-panel
docker-compose up -d
```

## 📚 Documentation

- **[Complete Tutorial](docs/TUTORIAL.md)** - Step-by-step setup and usage guide
- **[API Documentation](docs/API.md)** - Comprehensive REST API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Contributing Guide](docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Changelog](CHANGELOG.md)** - Version history and updates

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/CONTRIBUTING.md) for details.

### Quick Contribution Steps

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Complete guides and tutorials](docs/)
- **GitHub Issues**: [Report bugs and request features](https://github.com/expertdevux/streaming-panel/issues)
- **Discussions**: [Community Q&A and discussions](https://github.com/expertdevux/streaming-panel/discussions)

### Professional Support

For enterprise deployments, custom development, and professional support:

**ExpertDevUX Professional Services**
- Custom streaming solutions
- Performance optimization and scaling
- Integration development and consulting
- Training and technical consultation

Contact: support@expertdevux.com

## 🌟 Show Your Support

If this project helps you, please consider:
- ⭐ Starring the repository
- 🐛 Reporting bugs and suggesting features
- 📖 Contributing to documentation
- 💡 Sharing your use cases and success stories

---

**Built with expertise in modern web development, video streaming technology, and user experience design by ExpertDevUX.**