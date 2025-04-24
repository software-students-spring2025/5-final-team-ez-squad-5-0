// web-container/static/js/relationship-metrics.js

/**
 * Relationship Metrics Real-time Updates
 * This script handles real-time updates for relationship metrics
 */

class RelationshipMetrics {
    constructor(options) {
        this.options = Object.assign({
            partnerId: null,
            token: null,
            updateInterval: 30, // seconds
            apiEndpoint: '/api/ai/relationship-metrics/',
            elements: {
                enableButton: 'enable-real-time',
                statusElement: 'update-status',
                displayContainer: 'real-time-display'
            },
            timeWindow: {
                minutes: 5 // Default time window for real-time updates
            }
        }, options);

        this.isUpdating = false;
        this.updateIntervalId = null;

        // Initialize elements
        this.elements = {
            enableButton: document.getElementById(this.options.elements.enableButton),
            statusElement: document.getElementById(this.options.elements.statusElement),
            displayContainer: document.getElementById(this.options.elements.displayContainer)
        };

        // Initialize if all required elements exist
        if (this.validateElements()) {
            this.init();
        } else {
            console.error('Missing required elements for RelationshipMetrics', this.elements);
        }
    }

    validateElements() {
        // Check that all required elements exist
        return this.elements.enableButton &&
            this.elements.statusElement &&
            this.elements.displayContainer &&
            this.options.partnerId &&
            this.options.token;
    }

    init() {
        // Set up event listeners
        this.elements.enableButton.addEventListener('click', () => {
            this.toggleUpdates();
        });

        console.log('RelationshipMetrics initialized');
    }

    toggleUpdates() {
        if (!this.isUpdating) {
            this.startUpdates();
        } else {
            this.stopUpdates();
        }
    }

    startUpdates() {
        this.isUpdating = true;
        this.elements.enableButton.textContent = 'Disable Real-time Updates';
        this.elements.statusElement.textContent = 'Updates active';
        this.elements.statusElement.className = 'update-status active';

        // Fetch initial update
        this.fetchMetrics();

        // Set interval for regular updates
        this.updateIntervalId = setInterval(() => {
            this.fetchMetrics();
        }, this.options.updateInterval * 1000);

        console.log('Started real-time updates');
    }

    stopUpdates() {
        this.isUpdating = false;
        this.elements.enableButton.textContent = 'Enable Real-time Updates';
        this.elements.statusElement.textContent = 'Updates disabled';
        this.elements.statusElement.className = 'update-status';

        // Clear interval
        if (this.updateIntervalId) {
            clearInterval(this.updateIntervalId);
            this.updateIntervalId = null;
        }

        console.log('Stopped real-time updates');
    }

    fetchMetrics() {
        // Show loading indicator
        this.elements.displayContainer.innerHTML = '<div class="loading">Updating metrics...</div>';

        // Build query parameters
        const timeParams = [];
        if (this.options.timeWindow.days) {
            timeParams.push(`days=${this.options.timeWindow.days}`);
        }
        if (this.options.timeWindow.hours) {
            timeParams.push(`hours=${this.options.timeWindow.hours}`);
        }
        if (this.options.timeWindow.minutes) {
            timeParams.push(`minutes=${this.options.timeWindow.minutes}`);
        }

        const queryString = timeParams.length > 0 ? `?${timeParams.join('&')}` : `?minutes=${this.options.timeWindow.minutes}`;

        // Fetch the latest metrics
        fetch(`${this.options.apiEndpoint}${this.options.partnerId}${queryString}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${this.options.token}`,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Update the display with real-time metrics
                const metrics = data.metrics || {};
                const insights = data.insights || [];
                const timestamp = new Date().toLocaleTimeString();

                // Format the metrics for display
                let metricsHtml = `
                <div class="real-time-header">
                    <h4>Last ${this.options.timeWindow.minutes} Minutes Activity</h4>
                    <div class="last-updated">Last updated: ${timestamp}</div>
                </div>
                <div class="real-time-metrics">
                    <div class="rt-metric">
                        <div class="rt-metric-label">Messages</div>
                        <div class="rt-metric-value">${metrics.message_count || 0}</div>
                    </div>
                    <div class="rt-metric">
                        <div class="rt-metric-label">Avg Response</div>
                        <div class="rt-metric-value">${metrics.avg_response_time ? Math.round(metrics.avg_response_time * 10) / 10 + ' min' : 'N/A'}</div>
                    </div>
                    <div class="rt-metric">
                        <div class="rt-metric-label">Frequency</div>
                        <div class="rt-metric-value">${Math.round((metrics.message_frequency || 0) * 10) / 10} ${metrics.frequency_unit || 'per min'}</div>
                    </div>
                </div>
            `;

                // Add sentiment distribution if available
                if (metrics.sentiment_distribution) {
                    const sentiments = metrics.sentiment_distribution;
                    metricsHtml += `
                    <div class="rt-sentiment">
                        <h5>Message Sentiment</h5>
                        <div class="rt-sentiment-bar">
                            <div class="sentiment-segment positive" style="--width: ${Math.round(sentiments.positive || 0)}%" title="Positive: ${Math.round(sentiments.positive || 0)}%">
                                ${Math.round(sentiments.positive || 0)}%
                            </div>
                            <div class="sentiment-segment neutral" style="--width: ${Math.round(sentiments.neutral || 0)}%" title="Neutral: ${Math.round(sentiments.neutral || 0)}%">
                                ${Math.round(sentiments.neutral || 0)}%
                            </div>
                            <div class="sentiment-segment negative" style="--width: ${Math.round(sentiments.negative || 0)}%" title="Negative: ${Math.round(sentiments.negative || 0)}%">
                                ${Math.round(sentiments.negative || 0)}%
                            </div>
                        </div>
                    </div>
                `;
                }

                // Add recent insights if available (up to 2)
                if (insights && insights.length > 0) {
                    metricsHtml += `<div class="rt-insights"><h5>Recent Insights</h5>`;

                    // Show up to 2 insights
                    const displayInsights = insights.slice(0, 2);

                    displayInsights.forEach(insight => {
                        metricsHtml += `
                        <div class="rt-insight-card ${insight.type || 'general'}">
                            <p class="rt-insight-text">${insight.text || 'No insight text'}</p>
                        </div>
                    `;
                    });

                    metricsHtml += `</div>`;
                }

                // Update the display
                this.elements.displayContainer.innerHTML = metricsHtml;
            })
            .catch(error => {
                this.elements.displayContainer.innerHTML = `<div class="error">Error fetching real-time metrics: ${error.message}. Try again later.</div>`;
                console.error('Error fetching real-time metrics:', error);

                // If there was an error, stop the updates to prevent continuous error messages
                if (this.isUpdating) {
                    console.log('Stopping updates due to error');
                    this.stopUpdates();
                }
            });
    }
}

// If this script is loaded in a CommonJS or ES module environment
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = RelationshipMetrics;
}