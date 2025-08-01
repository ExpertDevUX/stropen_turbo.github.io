// Dashboard functionality for stream management

class StreamDashboard {
    constructor() {
        this.streams = new Map();
        this.statsChart = null;
        this.livePreviewPlayers = new Map();
        this.init();
    }

    init() {
        this.bindEvents();
        this.startStatusUpdates();
        this.loadStreams();
        this.loadRTMPStatus();
        this.initializeLivePreviews();
    }

    bindEvents() {
        // Stream control buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('stream-control')) {
                this.handleStreamControl(e.target);
            }
        });

        // Copy buttons
        document.addEventListener('click', (e) => {
            if (e.target.getAttribute('onclick')?.includes('copyToClipboard')) {
                this.handleCopyClick(e.target);
            }
        });
    }

    async handleStreamControl(button) {
        const streamId = button.dataset.streamId;
        const action = button.dataset.action;

        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner"></span> ' + 
                          (action === 'start' ? 'Starting...' : 'Stopping...');

        try {
            const response = await fetch(`/stream/${streamId}/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showToast(result.message, 'success');
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                this.showToast(result.message, 'error');
                button.disabled = false;
                this.resetButton(button, action);
            }
        } catch (error) {
            console.error('Error controlling stream:', error);
            this.showToast('Failed to ' + action + ' stream', 'error');
            button.disabled = false;
            this.resetButton(button, action);
        }
    }

    resetButton(button, action) {
        const icon = action === 'start' ? 'fas fa-play' : 'fas fa-stop';
        const text = action === 'start' ? 'Start' : 'Stop';
        button.innerHTML = `<i class="${icon}"></i> ${text}`;
    }

    async loadStreams() {
        // This would load stream data if needed
        // For now, streams are rendered server-side
    }

    startStatusUpdates() {
        // Update stream statuses every 30 seconds
        setInterval(() => {
            this.updateStreamStatuses();
            this.updateLivePreviews();
        }, 30000);
    }

    async updateStreamStatuses() {
        const streamCards = document.querySelectorAll('[data-stream-id]');
        
        for (const card of streamCards) {
            const streamId = card.dataset.streamId;
            try {
                const response = await fetch(`/stream/${streamId}/status`);
                const status = await response.json();
                
                this.updateStreamCard(streamId, status);
            } catch (error) {
                console.error(`Error updating status for stream ${streamId}:`, error);
            }
        }
    }

    updateStreamCard(streamId, status) {
        const updateElement = document.getElementById(`last-update-${streamId}`);
        if (updateElement) {
            const now = new Date();
            updateElement.textContent = now.toLocaleTimeString();
        }

        // Update status badge if needed
        const statusBadge = document.querySelector(`[data-stream-id="${streamId}"] .badge`);
        if (statusBadge && status.status) {
            statusBadge.textContent = status.status.charAt(0).toUpperCase() + status.status.slice(1);
            statusBadge.className = `badge bg-${status.status === 'running' ? 'success' : 'secondary'}`;
        }
    }

    showToast(message, type = 'info') {
        const toastContainer = this.getOrCreateToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove toast element after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    getOrCreateToastContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '1050';
            document.body.appendChild(container);
        }
        return container;
    }

    handleCopyClick(button) {
        // Add visual feedback for copy actions
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-check"></i> Copied!';
        button.classList.add('btn-success');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('btn-success');
        }, 2000);
    }

    // RTMP Server Management
    async loadRTMPStatus() {
        try {
            const response = await fetch('/rtmp/status');
            const status = await response.json();
            this.updateRTMPStatus(status);
        } catch (error) {
            console.error('Error loading RTMP status:', error);
            this.updateRTMPStatus({ running: false, error: true });
        }
    }

    updateRTMPStatus(status) {
        const statusBadge = document.getElementById('rtmp-server-status');
        const statusText = document.getElementById('rtmp-status-text');
        const serverBtn = document.getElementById('rtmp-server-btn');
        const activeStreamsCount = document.getElementById('active-streams-count');
        const serverPort = document.getElementById('server-port');
        const detailedStatus = document.getElementById('detailed-server-status');

        if (status.running) {
            statusBadge.textContent = 'Online';
            statusBadge.className = 'badge bg-success text-white ms-2';
            statusText.textContent = 'Stop RTMP';
            serverBtn.className = 'btn btn-outline-warning';
        } else {
            statusBadge.textContent = 'Offline';
            statusBadge.className = 'badge bg-secondary text-white ms-2';
            statusText.textContent = 'Start RTMP';
            serverBtn.className = 'btn btn-outline-success';
        }

        if (activeStreamsCount) activeStreamsCount.textContent = status.active_streams || 0;
        if (serverPort) serverPort.textContent = status.port || 1935;
        if (detailedStatus) detailedStatus.textContent = status.running ? 'Running' : 'Stopped';
    }

    async toggleRTMPServer() {
        const serverBtn = document.getElementById('rtmp-server-btn');
        const statusBadge = document.getElementById('rtmp-server-status');
        const isRunning = statusBadge.textContent === 'Online';
        
        serverBtn.disabled = true;
        serverBtn.innerHTML = '<span class="loading-spinner"></span> Processing...';

        try {
            const endpoint = isRunning ? '/rtmp/stop' : '/rtmp/start';
            const response = await fetch(endpoint, { method: 'POST' });
            const result = await response.json();

            if (result.status === 'success') {
                this.showToast(result.message, 'success');
                // Refresh status after a short delay
                setTimeout(() => this.loadRTMPStatus(), 1000);
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            console.error('Error toggling RTMP server:', error);
            this.showToast('Failed to toggle RTMP server', 'error');
        } finally {
            serverBtn.disabled = false;
            // Status will be updated by loadRTMPStatus
        }
    }

    copyRTMPUrl() {
        const rtmpUrl = `rtmp://${window.location.host}/live/`;
        navigator.clipboard.writeText(rtmpUrl).then(() => {
            this.showToast('RTMP URL copied to clipboard', 'success');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = rtmpUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            this.showToast('RTMP URL copied to clipboard', 'success');
        });
    }

    // Live Preview Functionality
    initializeLivePreviews() {
        const streamCards = document.querySelectorAll('[data-stream-id]');
        streamCards.forEach(card => {
            const streamId = card.dataset.streamId;
            this.createLivePreview(streamId, card);
        });
    }

    createLivePreview(streamId, cardElement) {
        // Find or create preview container
        let previewContainer = cardElement.querySelector('.live-preview-container');
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'live-preview-container';
            previewContainer.innerHTML = `
                <div class="stream-thumbnail position-relative">
                    <video id="preview-${streamId}" 
                           class="w-100 h-100 rounded" 
                           style="object-fit: cover; max-height: 120px; background: #000;"
                           muted autoplay playsinline>
                    </video>
                    <div class="position-absolute top-0 end-0 m-2">
                        <span class="badge bg-danger live-indicator" style="display: none;">
                            <i class="fas fa-circle" style="animation: pulse 2s infinite;"></i> LIVE
                        </span>
                    </div>
                    <div class="position-absolute bottom-0 start-0 end-0 p-2 bg-dark bg-opacity-75 text-white text-center stream-offline-message">
                        <small><i class="fas fa-video-slash"></i> Stream Offline</small>
                    </div>
                </div>
            `;
            
            // Insert preview container before card body
            const cardBody = cardElement.querySelector('.card-body');
            cardBody.parentNode.insertBefore(previewContainer, cardBody);
        }

        this.setupLivePreviewPlayer(streamId);
    }

    async setupLivePreviewPlayer(streamId) {
        try {
            // Get embed info for the stream
            const response = await fetch(`/stream/${streamId}/status`);
            const streamData = await response.json();

            if (streamData.status === 'running') {
                this.loadLivePreview(streamId);
            } else {
                this.showOfflinePreview(streamId);
            }
        } catch (error) {
            console.error(`Error setting up preview for stream ${streamId}:`, error);
            this.showOfflinePreview(streamId);
        }
    }

    async loadLivePreview(streamId) {
        const video = document.getElementById(`preview-${streamId}`);
        const liveIndicator = document.querySelector(`[data-stream-id="${streamId}"] .live-indicator`);
        const offlineMessage = document.querySelector(`[data-stream-id="${streamId}"] .stream-offline-message`);

        if (!video) return;

        try {
            // Try to load HLS stream for preview
            const hlsUrl = `/static/streams/hls/stream_${streamId}_720p.m3u8`;
            
            if (Hls.isSupported()) {
                let hls = this.livePreviewPlayers.get(streamId);
                if (hls) {
                    hls.destroy();
                }
                
                hls = new Hls({
                    enableWorker: false,
                    lowLatencyMode: true,
                    liveSyncDurationCount: 1,
                    liveMaxLatencyDurationCount: 3
                });
                
                hls.loadSource(hlsUrl);
                hls.attachMedia(video);
                
                hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    video.play().catch(e => console.log('Autoplay prevented:', e));
                    liveIndicator.style.display = 'block';
                    offlineMessage.style.display = 'none';
                });

                hls.on(Hls.Events.ERROR, (event, data) => {
                    if (data.fatal) {
                        this.showOfflinePreview(streamId);
                    }
                });

                this.livePreviewPlayers.set(streamId, hls);
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                // Safari native HLS support
                video.src = hlsUrl;
                video.addEventListener('loadedmetadata', () => {
                    video.play().catch(e => console.log('Autoplay prevented:', e));
                    liveIndicator.style.display = 'block';
                    offlineMessage.style.display = 'none';
                });
                video.addEventListener('error', () => {
                    this.showOfflinePreview(streamId);
                });
            } else {
                this.showOfflinePreview(streamId);
            }
        } catch (error) {
            console.error(`Error loading live preview for stream ${streamId}:`, error);
            this.showOfflinePreview(streamId);
        }
    }

    showOfflinePreview(streamId) {
        const video = document.getElementById(`preview-${streamId}`);
        const liveIndicator = document.querySelector(`[data-stream-id="${streamId}"] .live-indicator`);
        const offlineMessage = document.querySelector(`[data-stream-id="${streamId}"] .stream-offline-message`);

        if (video) {
            video.src = '';
            video.load();
        }
        
        if (liveIndicator) liveIndicator.style.display = 'none';
        if (offlineMessage) offlineMessage.style.display = 'block';

        // Clean up HLS player
        const hls = this.livePreviewPlayers.get(streamId);
        if (hls) {
            hls.destroy();
            this.livePreviewPlayers.delete(streamId);
        }
    }

    updateLivePreviews() {
        const streamCards = document.querySelectorAll('[data-stream-id]');
        streamCards.forEach(card => {
            const streamId = card.dataset.streamId;
            this.setupLivePreviewPlayer(streamId);
        });
    }
}

// Global functions for modal interactions
function showEmbedCode(streamId) {
    const modal = new bootstrap.Modal(document.getElementById('embedModal'));
    const embedCode = document.getElementById('embedCode');
    const directLink = document.getElementById('directLink');

    const baseUrl = window.location.origin;
    const embedUrl = `${baseUrl}/stream/${streamId}/embed`;
    const playerUrl = `${baseUrl}/stream/${streamId}/player`;

    embedCode.value = `<iframe src="${embedUrl}" width="800" height="450" frameborder="0" allowfullscreen></iframe>`;
    directLink.value = playerUrl;

    modal.show();
}

function showStats(streamId) {
    const modal = new bootstrap.Modal(document.getElementById('statsModal'));
    modal.show();

    // Load and display stats
    loadStreamStats(streamId);
}

async function loadStreamStats(streamId) {
    try {
        const response = await fetch(`/stream/${streamId}/stats`);
        const data = await response.json();

        if (data.stats && data.stats.length > 0) {
            renderStatsChart(data.stats);
        } else {
            // Show no data message
            const chartContainer = document.getElementById('statsChart').getContext('2d');
            if (window.statsChart) {
                window.statsChart.destroy();
            }
            
            // Create empty chart with message
            window.statsChart = new Chart(chartContainer, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: []
                },
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'No statistics available yet'
                        }
                    }
                }
            });
        }
    } catch (error) {
        console.error('Error loading stream stats:', error);
    }
}

function renderStatsChart(stats) {
    const ctx = document.getElementById('statsChart').getContext('2d');
    
    if (window.statsChart) {
        window.statsChart.destroy();
    }

    const labels = stats.map(stat => {
        const date = new Date(stat.timestamp);
        return date.toLocaleTimeString();
    }).reverse();

    const bitrateData = stats.map(stat => stat.bitrate).reverse();
    const fpsData = stats.map(stat => stat.frame_rate).reverse();
    const viewersData = stats.map(stat => stat.viewers).reverse();

    window.statsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Bitrate (kbps)',
                    data: bitrateData,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    yAxisID: 'y'
                },
                {
                    label: 'FPS',
                    data: fpsData,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    yAxisID: 'y1'
                },
                {
                    label: 'Viewers',
                    data: viewersData,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    yAxisID: 'y2'
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Bitrate (kbps)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'FPS'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                },
                y2: {
                    type: 'linear',
                    display: false,
                    position: 'right'
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Stream Statistics'
                }
            }
        }
    });
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    element.setSelectionRange(0, 99999); // For mobile devices
    
    try {
        document.execCommand('copy');
        return true;
    } catch (err) {
        console.error('Failed to copy: ', err);
        return false;
    }
}

// Global functions for RTMP server management
function toggleRTMPServer() {
    if (window.streamDashboard) {
        window.streamDashboard.toggleRTMPServer();
    }
}

function refreshRTMPStatus() {
    if (window.streamDashboard) {
        window.streamDashboard.loadRTMPStatus();
    }
}

function copyRTMPUrlToClipboard() {
    if (window.streamDashboard) {
        window.streamDashboard.copyRTMPUrl();
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.streamDashboard = new StreamDashboard();
});