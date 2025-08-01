# Advanced Streaming Panel - API Documentation

Complete REST API documentation for the Advanced Streaming Panel platform.

## Base URL

```
https://your-domain.com/api/v1
```

## Authentication

All API endpoints require authentication using JWT tokens or API keys.

### Get Authentication Token

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Using Token

Include the token in the Authorization header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

## Stream Management

### List Streams

```bash
GET /api/streams
```

**Response:**
```json
{
  "streams": [
    {
      "id": 1,
      "name": "Tutorial Stream",
      "status": "running",
      "input_url": "rtmp://localhost:1935/live/tutorial",
      "latency_mode": "tutorial",
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-01T10:30:00Z",
      "destinations": [
        {
          "platform": "tutorial",
          "status": "active"
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}
```

### Get Stream Details

```bash
GET /api/streams/{stream_id}
```

**Response:**
```json
{
  "id": 1,
  "name": "Tutorial Stream",
  "status": "running",
  "input_url": "rtmp://localhost:1935/live/tutorial",
  "input_type": "rtmp",
  "latency_mode": "tutorial",
  "record_enabled": true,
  "video_codec": "h264",
  "audio_codec": "aac",
  "bitrate_mode": "cbr",
  "keyframe_interval": 2,
  "outputs": [
    {
      "format_type": "hls",
      "resolution": "720p",
      "bitrate": 2500,
      "output_path": "/static/streams/hls/stream_1_720p.m3u8"
    }
  ],
  "destinations": [
    {
      "name": "Tutorial Platform",
      "platform": "tutorial",
      "rtmp_url": "rtmp://tutorial-platform.com/live/",
      "enabled": true
    }
  ],
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:30:00Z"
}
```

### Create Stream

```bash
POST /api/streams
Content-Type: application/json

{
  "name": "My Tutorial Stream",
  "input_url": "rtmp://localhost:1935/live/my_stream",
  "input_type": "rtmp",
  "latency_mode": "tutorial",
  "record_enabled": true,
  "video_codec": "h264",
  "audio_codec": "aac",
  "qualities": ["720p", "480p", "360p"],
  "destinations": [
    {
      "name": "Tutorial Platform",
      "platform": "tutorial",
      "rtmp_url": "rtmp://tutorial-platform.com/live/",
      "stream_key": "your_stream_key"
    }
  ]
}
```

**Response:**
```json
{
  "id": 2,
  "name": "My Tutorial Stream",
  "status": "stopped",
  "message": "Stream created successfully"
}
```

### Update Stream

```bash
PUT /api/streams/{stream_id}
Content-Type: application/json

{
  "name": "Updated Stream Name",
  "latency_mode": "low",
  "record_enabled": false
}
```

### Delete Stream

```bash
DELETE /api/streams/{stream_id}
```

**Response:**
```json
{
  "message": "Stream deleted successfully"
}
```

### Start Stream

```bash
POST /api/streams/{stream_id}/start
```

**Response:**
```json
{
  "status": "success",
  "message": "Stream started successfully",
  "stream_id": 1,
  "outputs": [
    {
      "format": "hls",
      "url": "https://your-domain.com/static/streams/hls/stream_1_720p.m3u8"
    },
    {
      "format": "dash",
      "url": "https://your-domain.com/static/streams/dash/stream_1_720p.mpd"
    }
  ]
}
```

### Stop Stream

```bash
POST /api/streams/{stream_id}/stop
```

**Response:**
```json
{
  "status": "success",
  "message": "Stream stopped successfully",
  "stream_id": 1
}
```

### Get Stream Status

```bash
GET /api/streams/{stream_id}/status
```

**Response:**
```json
{
  "stream_id": 1,
  "status": "running",
  "uptime": 3600,
  "current_viewers": 25,
  "peak_viewers": 45,
  "output_bitrate": 2500,
  "input_bitrate": 2800,
  "frame_rate": 30.0,
  "resolution": "1280x720",
  "last_updated": "2025-01-01T11:00:00Z"
}
```

### Get Stream Statistics

```bash
GET /api/streams/{stream_id}/stats
```

**Query Parameters:**
- `start_time`: ISO 8601 timestamp
- `end_time`: ISO 8601 timestamp
- `interval`: `1m`, `5m`, `1h`, `1d`

**Response:**
```json
{
  "stream_id": 1,
  "stats": [
    {
      "timestamp": "2025-01-01T10:00:00Z",
      "viewers": 15,
      "bitrate": 2500.0,
      "frame_rate": 30.0,
      "packet_loss": 0.1
    },
    {
      "timestamp": "2025-01-01T10:05:00Z",
      "viewers": 20,
      "bitrate": 2480.0,
      "frame_rate": 29.8,
      "packet_loss": 0.2
    }
  ],
  "summary": {
    "avg_viewers": 17.5,
    "peak_viewers": 25,
    "avg_bitrate": 2490.0,
    "uptime": 3600
  }
}
```

## RTMP Server Management

### Get RTMP Server Status

```bash
GET /api/rtmp/status
```

**Response:**
```json
{
  "running": true,
  "port": 1935,
  "active_streams": 3,
  "total_connections": 15,
  "uptime": 86400,
  "version": "1.2.1",
  "streams": [
    {
      "stream_key": "tutorial_stream",
      "client_ip": "192.168.1.100",
      "connected_at": "2025-01-01T10:00:00Z",
      "bitrate": 2500
    }
  ]
}
```

### Start RTMP Server

```bash
POST /api/rtmp/start
```

**Response:**
```json
{
  "status": "success",
  "message": "RTMP server started successfully",
  "port": 1935,
  "url": "rtmp://your-domain.com:1935/live/"
}
```

### Stop RTMP Server

```bash
POST /api/rtmp/stop
```

**Response:**
```json
{
  "status": "success",
  "message": "RTMP server stopped successfully"
}
```

### RTMP Authentication

```bash
POST /api/rtmp/auth
Content-Type: application/x-www-form-urlencoded

name=stream_key&addr=192.168.1.100&app=live
```

**Response:**
```
HTTP/1.1 200 OK (Allow)
HTTP/1.1 403 Forbidden (Deny)
```

## Destinations Management

### List Destinations

```bash
GET /api/destinations
```

**Response:**
```json
{
  "destinations": [
    {
      "id": 1,
      "name": "Tutorial Platform",
      "platform": "tutorial",
      "rtmp_url": "rtmp://tutorial-platform.com/live/",
      "enabled": true,
      "created_at": "2025-01-01T09:00:00Z"
    },
    {
      "id": 2,
      "name": "YouTube Live",
      "platform": "youtube",
      "rtmp_url": "rtmp://a.rtmp.youtube.com/live2/",
      "enabled": true,
      "created_at": "2025-01-01T09:15:00Z"
    }
  ]
}
```

### Create Destination

```bash
POST /api/destinations
Content-Type: application/json

{
  "name": "My YouTube Channel",
  "platform": "youtube",
  "rtmp_url": "rtmp://a.rtmp.youtube.com/live2/",
  "stream_key": "your-youtube-stream-key",
  "enabled": true
}
```

### Update Destination

```bash
PUT /api/destinations/{destination_id}
Content-Type: application/json

{
  "name": "Updated Channel Name",
  "enabled": false
}
```

### Delete Destination

```bash
DELETE /api/destinations/{destination_id}
```

## Analytics and Reporting

### Get Dashboard Analytics

```bash
GET /api/analytics/dashboard
```

**Query Parameters:**
- `period`: `24h`, `7d`, `30d`, `90d`

**Response:**
```json
{
  "period": "24h",
  "total_streams": 5,
  "active_streams": 2,
  "total_viewers": 150,
  "peak_concurrent_viewers": 45,
  "total_watch_time": 7200,
  "average_watch_time": 480,
  "stream_metrics": [
    {
      "stream_id": 1,
      "name": "Tutorial Stream",
      "viewers": 25,
      "watch_time": 3600,
      "engagement_rate": 0.85
    }
  ],
  "platform_distribution": {
    "tutorial": 45,
    "youtube": 30,
    "twitch": 25
  },
  "geographic_distribution": {
    "US": 40,
    "EU": 35,
    "Asia": 25
  }
}
```

### Get Stream Analytics

```bash
GET /api/analytics/streams/{stream_id}
```

**Query Parameters:**
- `start_date`: YYYY-MM-DD
- `end_date`: YYYY-MM-DD
- `metrics`: `viewers,bitrate,engagement`

**Response:**
```json
{
  "stream_id": 1,
  "name": "Tutorial Stream",
  "period": {
    "start": "2025-01-01",
    "end": "2025-01-07"
  },
  "metrics": {
    "total_sessions": 125,
    "unique_viewers": 95,
    "total_watch_time": 14400,
    "average_session_duration": 480,
    "peak_concurrent_viewers": 35,
    "engagement_rate": 0.78,
    "quality_metrics": {
      "average_bitrate": 2450.0,
      "buffer_rate": 0.02,
      "startup_time": 1.2
    }
  },
  "timeline": [
    {
      "timestamp": "2025-01-01T00:00:00Z",
      "viewers": 0,
      "bitrate": 0,
      "engagement": 0
    }
  ]
}
```

## User Management

### List Users

```bash
GET /api/users
```

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "administrator",
      "created_at": "2025-01-01T00:00:00Z",
      "last_login": "2025-01-01T10:00:00Z"
    }
  ]
}
```

### Create User

```bash
POST /api/users
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "secure_password",
  "role": "user"
}
```

### Update User

```bash
PUT /api/users/{user_id}
Content-Type: application/json

{
  "email": "newemail@example.com",
  "role": "moderator"
}
```

## System Information

### Get System Status

```bash
GET /api/system/status
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.1.0",
  "uptime": 86400,
  "system": {
    "cpu_usage": 25.5,
    "memory_usage": 45.2,
    "disk_usage": 30.1,
    "load_average": [1.2, 1.5, 1.8]
  },
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "nginx": "healthy",
    "rtmp_server": "running"
  },
  "performance": {
    "active_streams": 3,
    "total_bandwidth": 7500,
    "concurrent_viewers": 75
  }
}
```

### Get System Health

```bash
GET /api/system/health
```

**Response:**
```json
{
  "status": "healthy",
  "checks": {
    "database": {
      "status": "healthy",
      "response_time": 15,
      "last_check": "2025-01-01T12:00:00Z"
    },
    "redis": {
      "status": "healthy",
      "response_time": 2,
      "last_check": "2025-01-01T12:00:00Z"
    },
    "storage": {
      "status": "healthy",
      "free_space": "150GB",
      "total_space": "200GB"
    },
    "network": {
      "status": "healthy",
      "bandwidth_available": "100Mbps",
      "bandwidth_used": "25Mbps"
    }
  }
}
```

## Webhooks

### Stream Events

Configure webhook URLs to receive real-time stream events:

#### Stream Started

```json
POST https://your-webhook-url.com/stream-started

{
  "event": "stream.started",
  "timestamp": "2025-01-01T10:00:00Z",
  "stream_id": 1,
  "stream_name": "Tutorial Stream",
  "input_url": "rtmp://localhost:1935/live/tutorial"
}
```

#### Stream Stopped

```json
POST https://your-webhook-url.com/stream-stopped

{
  "event": "stream.stopped",
  "timestamp": "2025-01-01T11:00:00Z",
  "stream_id": 1,
  "stream_name": "Tutorial Stream",
  "duration": 3600,
  "peak_viewers": 45
}
```

#### Viewer Threshold

```json
POST https://your-webhook-url.com/viewer-threshold

{
  "event": "viewers.threshold",
  "timestamp": "2025-01-01T10:30:00Z",
  "stream_id": 1,
  "current_viewers": 100,
  "threshold": 100,
  "type": "exceeded"
}
```

## Rate Limiting

API requests are rate limited:

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour
- **Streaming operations**: 60 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 995
X-RateLimit-Reset: 1640995200
```

## Error Handling

### Error Response Format

```json
{
  "error": {
    "code": "STREAM_NOT_FOUND",
    "message": "Stream with ID 999 not found",
    "details": {
      "stream_id": 999,
      "requested_at": "2025-01-01T12:00:00Z"
    }
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Invalid or missing authentication |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid input data |
| `RATE_LIMITED` | 429 | Too many requests |
| `STREAM_NOT_FOUND` | 404 | Stream doesn't exist |
| `STREAM_ALREADY_RUNNING` | 409 | Stream is already active |
| `RTMP_SERVER_ERROR` | 500 | RTMP server operation failed |
| `ENCODING_ERROR` | 500 | Video encoding failed |

## SDK Examples

### Python SDK

```python
import requests

class StreamingPanelAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def create_stream(self, name, input_url, latency_mode='tutorial'):
        data = {
            'name': name,
            'input_url': input_url,
            'latency_mode': latency_mode,
            'qualities': ['720p', '480p']
        }
        response = requests.post(
            f'{self.base_url}/api/streams',
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def start_stream(self, stream_id):
        response = requests.post(
            f'{self.base_url}/api/streams/{stream_id}/start',
            headers=self.headers
        )
        return response.json()

# Usage
api = StreamingPanelAPI('https://your-domain.com', 'your-token')
stream = api.create_stream('My Stream', 'rtmp://localhost:1935/live/test')
result = api.start_stream(stream['id'])
```

### JavaScript SDK

```javascript
class StreamingPanelAPI {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async createStream(name, inputUrl, latencyMode = 'tutorial') {
        const response = await fetch(`${this.baseUrl}/api/streams`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                name,
                input_url: inputUrl,
                latency_mode: latencyMode,
                qualities: ['720p', '480p']
            })
        });
        return response.json();
    }
    
    async startStream(streamId) {
        const response = await fetch(`${this.baseUrl}/api/streams/${streamId}/start`, {
            method: 'POST',
            headers: this.headers
        });
        return response.json();
    }
}

// Usage
const api = new StreamingPanelAPI('https://your-domain.com', 'your-token');
const stream = await api.createStream('My Stream', 'rtmp://localhost:1935/live/test');
const result = await api.startStream(stream.id);
```

---

## Support

For API support and questions:

- **Documentation**: [https://docs.your-domain.com](https://docs.your-domain.com)
- **GitHub Issues**: [https://github.com/your-repo/streaming-panel/issues](https://github.com/your-repo/streaming-panel/issues)
- **Email Support**: api-support@expertdevux.com

---

*Copyright © 2025 Expert Dev UX. All rights reserved.*