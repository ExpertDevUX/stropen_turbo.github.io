# Overview

This is a comprehensive live video streaming platform optimized for tutorial and educational content delivery. The application supports various input formats (RTMP, SRT, WebRTC) and outputs streams in HLS and DASH formats with tutorial-optimized latency modes. It features live video previews in the dashboard, multi-destination streaming capabilities, and an embedded video player for cross-site integration.

# User Preferences

Preferred communication style: Simple, everyday language.
Primary destination platform: Tutorial mode for educational content
Copyright profile: ExpertDevUX professional development services

# System Architecture

## Backend Architecture

**Framework**: Flask-based web application with SQLAlchemy ORM for database operations. The application follows a modular structure with separate concerns for stream management, FFmpeg processing, and web routing.

**Database Design**: Uses SQLAlchemy with support for both SQLite (development) and PostgreSQL (production). The schema includes:
- `Stream` model for stream configurations and settings
- `StreamOutput` model for managing multiple quality outputs per stream
- `StreamStats` model for tracking viewer metrics and performance data
- Support for JSON fields to store complex configuration data

**Stream Processing**: Custom FFmpeg service wrapper that manages video encoding processes, handles multiple output formats simultaneously, and provides real-time monitoring of streaming processes through background threads.

**Configuration Management**: Centralized configuration system with predefined video encoding presets, quality profiles (240p to 1080p), and adaptive settings for low-latency, tutorial mode (optimized for educational content), and high-quality streaming modes.

## Frontend Architecture

**Template Engine**: Jinja2 templates with a responsive Bootstrap-based dark theme UI. The interface includes:
- Dashboard for stream overview and management
- Stream configuration forms with quality and destination selection
- Embedded video player with multi-format support
- Real-time status updates and statistics visualization

**Client-Side Features**: Video.js-based player with HLS/DASH support, live video preview thumbnails with HLS.js integration, real-time stream statistics using Chart.js, and interactive controls for quality switching and stream management.

## Stream Management

**Multi-Destination Support**: Streams can be configured to output to multiple platforms simultaneously including tutorial platform, YouTube, Twitch, Facebook, and Instagram with different quality settings for each destination.

**Adaptive Streaming**: Supports both HLS and DASH protocols with configurable segment durations and playlist sizes optimized for different latency requirements.

**Quality Control**: Multiple resolution outputs (240p to 1080p) with configurable bitrates, encoding presets ranging from ultrafast to slow, and dynamic quality switching capabilities.

# External Dependencies

**Video Processing**: FFmpeg for video encoding, transcoding, and stream processing with support for hardware acceleration and multiple output formats.

**Database**: SQLAlchemy ORM with support for SQLite (development) and PostgreSQL (production environments).

**Frontend Libraries**: 
- Bootstrap for responsive UI components
- Video.js for HTML5 video playback with HLS/DASH support
- Chart.js for real-time statistics visualization
- Font Awesome for iconography

**Streaming Protocols**: Support for RTMP, SRT, and WebRTC input streams with HLS and DASH output formats for cross-platform compatibility.

**Infrastructure**: Designed to work with reverse proxy configurations and supports containerized deployment with appropriate middleware for production environments.