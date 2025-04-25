// web-container/static/js/real-time-insights.js
class RealTimeInsights {
    constructor(options) {
        this.options = Object.assign({
            socketUrl: 'http://localhost:5002',  // AI service URL
            partnerId: null,
            token: null,
            elements: {
                insightsContainer: 'real-time-insights',
                sentimentChart: 'sentiment-chart',
                messageCount: 'message-count',
                responseTime: 'response-time',
                messageFrequency: 'message-frequency',
                statusIndicator: 'connection-status',
                timeWindowSelector: 'time-window-selector'
            },
            defaultTimeWindow: {
                minutes: 5  // Default 5 minutes for real-time
            }
        }, options);

        // Time window options
        this.timeWindows = [
            { name: 'Real-time (5 min)', minutes: 5 },
            { name: 'Last 15 minutes', minutes: 15 },
            { name: 'Last hour', hours: 1 },
            { name: 'Last 3 hours', hours: 3 },
            { name: 'Today', hours: 24 },
            { name: 'Last 3 days', days: 3 },
            { name: 'Last week', days: 7 },
        ];

        this.socket = null;
        this.connected = false;
        this.authenticated = false;
        
        // Initialize if required parameters are present
        if (this.options.partnerId && this.options.token) {
            this.init();
        } else {
            console.error('Missing required parameters: partnerId or token');
        }
    }

    init() {
        this.setupInterface();
        this.connectSocket();
    }

    setupInterface() {
        // Setup time window selector
        const timeWindowSelector = document.getElementById(this.options.elements.timeWindowSelector);
        if (timeWindowSelector) {
            timeWindowSelector.innerHTML = '';
            
            this.timeWindows.forEach((window, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = window.name;
                timeWindowSelector.appendChild(option);
            });
            
            // Add event listener for changes
            timeWindowSelector.addEventListener('change', () => {
                const selectedIndex = parseInt(timeWindowSelector.value);
                this.updateTimeWindow(this.timeWindows[selectedIndex]);
            });
        }
        
        // Initialize status indicator
        this.updateStatus('Disconnected', 'offline');
    }

    connectSocket() {
        // Load Socket.IO from CDN if not available
        if (typeof io === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.4.1/socket.io.min.js';
            script.onload = () => this.setupSocketConnection();
            document.head.appendChild(script);
        } else {
            this.setupSocketConnection();
        }
    }

    setupSocketConnection() {
        // Connect to Socket.IO server
        this.socket = io(this.options.socketUrl);
        
        // Setup event handlers
        this.socket.on('connect', () => {
            this.connected = true;
            this.updateStatus('Connected', 'online');
            
            // Authenticate after connection
            this.socket.emit('authenticate', {
                token: this.options.token
            });
        });
        
        this.socket.on('disconnect', () => {
            this.connected = false;
            this.authenticated = false;
            this.updateStatus('Disconnected', 'offline');
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.updateStatus('Connection error', 'error');
        });
        
        this.socket.on('authenticated', (data) => {
            this.authenticated = true;
            this.updateStatus('Authenticated', 'authenticated');
            
            // Subscribe to real-time metrics
            this.subscribeToMetrics(this.options.defaultTimeWindow);
        });
        
        this.socket.on('authentication_error', (error) => {
            console.error('Authentication error:', error);
            this.updateStatus('Authentication failed', 'error');
        });
        
        this.socket.on('metrics_update', (data) => {
            this.updateMetricsDisplay(data);
        });
        
        this.socket.on('metrics_error', (error) => {
            console.error('Metrics error:', error);
            this.updateStatus('Error getting metrics', 'error');
        });
    }

    subscribeToMetrics(timeWindow) {
        if (this.connected && this.authenticated) {
            this.socket.emit('subscribe_metrics', {
                token: this.options.token,
                partner_id: this.options.partnerId,
                time_window: timeWindow
            });
        }
    }

    updateTimeWindow(timeWindow) {
        this.subscribeToMetrics(timeWindow);
        this.updateStatus('Updating metrics...', 'loading');
    }

    updateStatus(message, status) {
        const statusElement = document.getElementById(this.options.elements.statusIndicator);
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.className = `status-indicator ${status}`;
        }
    }

    updateMetricsDisplay(metrics) {
        // Update status with timestamp
        const timestamp = new Date(metrics.timestamp).toLocaleTimeString();
        this.updateStatus(`Updated at ${timestamp}`, 'success');
        
        // Update message count
        const messageCountElement = document.getElementById(this.options.elements.messageCount);
        if (messageCountElement) {
            messageCountElement.textContent = metrics.message_count;
            
            // Add breakdown if available
            if (metrics.user_percentage !== undefined) {
                const breakdown = document.createElement('div');
                breakdown.className = 'message-breakdown';
                breakdown.innerHTML = `
                    <div class="user-messages" style="width: ${metrics.user_percentage}%">You: ${Math.round(metrics.user_percentage)}%</div>
                    <div class="partner-messages" style="width: ${metrics.partner_percentage}%">Partner: ${Math.round(metrics.partner_percentage)}%</div>
                `;
                
                // Clear previous breakdown
                const existingBreakdown = messageCountElement.nextElementSibling;
                if (existingBreakdown && existingBreakdown.className === 'message-breakdown') {
                    existingBreakdown.remove();
                }
                
                messageCountElement.parentNode.insertBefore(breakdown, messageCountElement.nextSibling);
            }
        }
        
        // Update response time
        const responseTimeElement = document.getElementById(this.options.elements.responseTime);
        if (responseTimeElement) {
            if (metrics.avg_response_time) {
                responseTimeElement.textContent = `${Math.round(metrics.avg_response_time)} minutes`;
            } else {
                responseTimeElement.textContent = 'N/A';
            }
        }
        
        // Update message frequency
        const frequencyElement = document.getElementById(this.options.elements.messageFrequency);
        if (frequencyElement) {
            frequencyElement.textContent = `${metrics.message_frequency.toFixed(1)} ${metrics.frequency_unit}`;
        }
        
        // Update sentiment chart
        this.updateSentimentChart(metrics.sentiment_distribution);
        
        // Update insights
        this.updateInsights(metrics.insights || []);
    }

    updateSentimentChart(sentimentData) {
        const chartElement = document.getElementById(this.options.elements.sentimentChart);
        if (!chartElement) return;
        
        // Create chart with sentiment distribution
        chartElement.innerHTML = '';
        
        if (sentimentData) {
            const totalWidth = chartElement.clientWidth;
            
            const positiveWidth = (sentimentData.positive || 0) + '%';
            const neutralWidth = (sentimentData.neutral || 0) + '%';
            const negativeWidth = (sentimentData.negative || 0) + '%';
            
            chartElement.innerHTML = `
                <div class="sentiment-bar">
                    <div class="sentiment-segment positive" style="width: ${positiveWidth}" title="Positive: ${Math.round(sentimentData.positive || 0)}%">
                        ${Math.round(sentimentData.positive || 0)}%
                    </div>
                    <div class="sentiment-segment neutral" style="width: ${neutralWidth}" title="Neutral: ${Math.round(sentimentData.neutral || 0)}%">
                        ${Math.round(sentimentData.neutral || 0)}%
                    </div>
                    <div class="sentiment-segment negative" style="width: ${negativeWidth}" title="Negative: ${Math.round(sentimentData.negative || 0)}%">
                        ${Math.round(sentimentData.negative || 0)}%
                    </div>
                </div>
            `;
        } else {
            chartElement.innerHTML = '<div class="no-data">No sentiment data available</div>';
        }
    }

    updateInsights(insights) {
        const insightsContainer = document.getElementById(this.options.elements.insightsContainer);
        if (!insightsContainer) return;
        
        if (insights && insights.length > 0) {
            let insightsHtml = '';
            
            insights.forEach(insight => {
                insightsHtml += `
                    <div class="insight-card ${insight.type || ''}">
                        <div class="insight-content">
                            <p class="insight-text">${insight.text}</p>
                            <p class="insight-suggestion">${insight.suggestion}</p>
                        </div>
                    </div>
                `;
            });
            
            insightsContainer.innerHTML = insightsHtml;
        } else {
            insightsContainer.innerHTML = '<div class="no-insights">No insights available for this time period.</div>';
        }
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Expose to global scope
window.RealTimeInsights = RealTimeInsights;