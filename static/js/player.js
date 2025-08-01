// Video player functionality with multi-format support

class StreamPlayer {
    constructor() {
        this.player = null;
        this.currentFormat = 'hls';
        this.currentQuality = '';
        this.embedInfo = null;
        this.statsChart = null;
        this.statsInterval = null;
    }

    initialize(embedInfo) {
        this.embedInfo = embedInfo;
        this.setupPlayer();
        this.startStatsUpdates();
    }

    setupPlayer() {
        this.player = videojs('video-player', {
            techOrder: ['html5'],
            html5: {
                hls: {
                    enableLowInitialPlaylist: true,
                    smoothQualityChange: true,
                    overrideNative: true
                }
            },
            fluid: true,
            responsive: true,
            playbackRates: [0.5, 1, 1.25, 1.5, 2],
            plugins: {
                hotkeys: {
                    volumeStep: 0.1,
                    seekStep: 5,
                    enableModifiersForNumbers: false
                }
            }
        });

        this.player.ready(() => {
            console.log('Player is ready');
            this.loadInitialStream();
            this.setupEventListeners();
        });

        this.player.on('error', (error) => {
            console.error('Player error:', error);
            this.handlePlayerError(error);
        });

        this.player.on('loadstart', () => {
            console.log('Stream loading started');
        });

        this.player.on('loadeddata', () => {
            console.log('Stream data loaded');
        });

        this.player.on('play', () => {
            console.log('Playback started');
        });

        this.player.on('pause', () => {
            console.log('Playback paused');
        });
    }

    loadInitialStream() {
        if (this.embedInfo.status !== 'running') {
            this.showStreamOffline();
            return;
        }

        // Prefer HLS format
        if (this.embedInfo.hls_urls && this.embedInfo.hls_urls.length > 0) {
            this.currentFormat = 'hls';
            this.loadHLSStream();
        } else if (this.embedInfo.dash_urls && this.embedInfo.dash_urls.length > 0) {
            this.currentFormat = 'dash';
            this.loadDASHStream();
        } else {
            this.showNoStreamsAvailable();
        }

        this.updateFormatSelector();
        this.updateQualitySelector();
    }

    loadHLSStream() {
        const hlsUrls = this.embedInfo.hls_urls;
        if (hlsUrls.length === 0) return;

        // Start with highest quality available
        const selectedUrl = hlsUrls.find(url => url.quality === this.currentQuality) || hlsUrls[0];
        this.currentQuality = selectedUrl.quality;

        this.player.src({
            src: selectedUrl.url,
            type: 'application/x-mpegURL'
        });

        console.log(`Loading HLS stream: ${selectedUrl.url} (${selectedUrl.quality})`);
    }

    loadDASHStream() {
        const dashUrls = this.embedInfo.dash_urls;
        if (dashUrls.length === 0) return;

        // Start with highest quality available
        const selectedUrl = dashUrls.find(url => url.quality === this.currentQuality) || dashUrls[0];
        this.currentQuality = selectedUrl.quality;

        this.player.src({
            src: selectedUrl.url,
            type: 'application/dash+xml'
        });

        console.log(`Loading DASH stream: ${selectedUrl.url} (${selectedUrl.quality})`);
    }

    updateFormatSelector() {
        const formatSelect = document.getElementById('formatSelect');
        if (!formatSelect) return;

        formatSelect.innerHTML = '';

        if (this.embedInfo.hls_urls && this.embedInfo.hls_urls.length > 0) {
            const option = document.createElement('option');
            option.value = 'hls';
            option.textContent = 'HLS';
            option.selected = this.currentFormat === 'hls';
            formatSelect.appendChild(option);
        }

        if (this.embedInfo.dash_urls && this.embedInfo.dash_urls.length > 0) {
            const option = document.createElement('option');
            option.value = 'dash';
            option.textContent = 'DASH';
            option.selected = this.currentFormat === 'dash';
            formatSelect.appendChild(option);
        }
    }

    updateQualitySelector() {
        const qualitySelect = document.getElementById('qualitySelect');
        if (!qualitySelect) return;

        qualitySelect.innerHTML = '';

        const urls = this.currentFormat === 'hls' ? this.embedInfo.hls_urls : this.embedInfo.dash_urls;
        
        urls.forEach(url => {
            const option = document.createElement('option');
            option.value = url.quality;
            option.textContent = url.quality;
            option.selected = url.quality === this.currentQuality;
            qualitySelect.appendChild(option);
        });
    }

    switchFormat() {
        const formatSelect = document.getElementById('formatSelect');
        const newFormat = formatSelect.value;

        if (newFormat === this.currentFormat) return;

        const currentTime = this.player.currentTime();
        const wasPlaying = !this.player.paused();

        this.currentFormat = newFormat;
        
        if (newFormat === 'hls') {
            this.loadHLSStream();
        } else if (newFormat === 'dash') {
            this.loadDASHStream();
        }

        this.updateQualitySelector();

        // Restore playback position
        this.player.ready(() => {
            this.player.currentTime(currentTime);
            if (wasPlaying) {
                this.player.play();
            }
        });
    }

    switchQuality() {
        const qualitySelect = document.getElementById('qualitySelect');
        const newQuality = qualitySelect.value;

        if (newQuality === this.currentQuality) return;

        const currentTime = this.player.currentTime();
        const wasPlaying = !this.player.paused();

        this.currentQuality = newQuality;

        if (this.currentFormat === 'hls') {
            this.loadHLSStream();
        } else if (this.currentFormat === 'dash') {
            this.loadDASHStream();
        }

        // Restore playback position
        this.player.ready(() => {
            this.player.currentTime(currentTime);
            if (wasPlaying) {
                this.player.play();
            }
        });
    }

    toggleFullscreen() {
        if (this.player.isFullscreen()) {
            this.player.exitFullscreen();
        } else {
            this.player.requestFullscreen();
        }
    }

    refreshStream() {
        const currentTime = this.player.currentTime();
        const wasPlaying = !this.player.paused();

        // Reload current stream
        if (this.currentFormat === 'hls') {
            this.loadHLSStream();
        } else if (this.currentFormat === 'dash') {
            this.loadDASHStream();
        }

        // Try to restore position (may not work for live streams)
        this.player.ready(() => {
            if (currentTime > 0) {
                this.player.currentTime(currentTime);
            }
            if (wasPlaying) {
                this.player.play();
            }
        });
    }

    setupEventListeners() {
        // Quality change detection
        this.player.on('qualitychange', () => {
            console.log('Quality changed');
        });

        // Network state changes
        this.player.on('waiting', () => {
            console.log('Player is waiting for data');
        });

        this.player.on('canplay', () => {
            console.log('Player can start playing');
        });
    }

    handlePlayerError(error) {
        const errorCode = error.code || (this.player.error() && this.player.error().code);
        
        switch (errorCode) {
            case 1: // MEDIA_ERR_ABORTED
                console.log('Media playback aborted');
                break;
            case 2: // MEDIA_ERR_NETWORK
                console.log('Network error while loading media');
                this.showNetworkError();
                break;
            case 3: // MEDIA_ERR_DECODE
                console.log('Media decode error');
                this.showDecodeError();
                break;
            case 4: // MEDIA_ERR_SRC_NOT_SUPPORTED
                console.log('Media source not supported');
                this.showUnsupportedError();
                break;
            default:
                console.log('Unknown player error');
                this.showGenericError();
        }
    }

    showStreamOffline() {
        this.player.poster('/static/img/stream-offline.png');
        this.showMessage('Stream is currently offline', 'warning');
    }

    showNoStreamsAvailable() {
        this.showMessage('No stream formats available', 'error');
    }

    showNetworkError() {
        this.showMessage('Network error - check your connection', 'error');
    }

    showDecodeError() {
        this.showMessage('Unable to decode video - format may be unsupported', 'error');
    }

    showUnsupportedError() {
        this.showMessage('Video format not supported by your browser', 'error');
    }

    showGenericError() {
        this.showMessage('An error occurred while playing the video', 'error');
    }

    showMessage(message, type = 'info') {
        // This would show a message overlay on the player
        console.log(`${type.toUpperCase()}: ${message}`);
    }

    startStatsUpdates() {
        this.setupStatsChart();
        
        // Update stats every 10 seconds
        this.statsInterval = setInterval(() => {
            this.updateLiveStats();
        }, 10000);
    }

    setupStatsChart() {
        const canvas = document.getElementById('liveStatsChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        this.statsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Bitrate (kbps)',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.1
                    },
                    {
                        label: 'FPS',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: 'Live Stream Statistics'
                    }
                }
            }
        });
    }

    async updateLiveStats() {
        if (!this.embedInfo || !this.statsChart) return;

        try {
            const response = await fetch(`/stream/${this.embedInfo.stream_id}/stats`);
            const data = await response.json();

            if (data.stats && data.stats.length > 0) {
                // Get the latest 20 data points
                const recentStats = data.stats.slice(-20);
                
                const labels = recentStats.map(stat => {
                    const date = new Date(stat.timestamp);
                    return date.toLocaleTimeString();
                });

                const bitrateData = recentStats.map(stat => stat.bitrate);
                const fpsData = recentStats.map(stat => stat.frame_rate);

                this.statsChart.data.labels = labels;
                this.statsChart.data.datasets[0].data = bitrateData;
                this.statsChart.data.datasets[1].data = fpsData;
                
                this.statsChart.update('none'); // No animation for live updates
            }
        } catch (error) {
            console.error('Error updating live stats:', error);
        }
    }

    destroy() {
        if (this.statsInterval) {
            clearInterval(this.statsInterval);
        }
        
        if (this.statsChart) {
            this.statsChart.destroy();
        }
        
        if (this.player) {
            this.player.dispose();
        }
    }
}

// Global functions for template use
function initializePlayer(embedInfo) {
    window.streamPlayer = new StreamPlayer();
    window.streamPlayer.initialize(embedInfo);
}

function switchFormat() {
    if (window.streamPlayer) {
        window.streamPlayer.switchFormat();
    }
}

function switchQuality() {
    if (window.streamPlayer) {
        window.streamPlayer.switchQuality();
    }
}

function toggleFullscreen() {
    if (window.streamPlayer) {
        window.streamPlayer.toggleFullscreen();
    }
}

function refreshStream() {
    if (window.streamPlayer) {
        window.streamPlayer.refreshStream();
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (window.streamPlayer) {
        window.streamPlayer.destroy();
    }
});
