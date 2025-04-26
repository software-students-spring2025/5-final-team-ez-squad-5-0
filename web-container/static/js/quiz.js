// static/js/quiz.js
document.addEventListener('DOMContentLoaded', function() {
    const scoreEl = document.getElementById('score-circle');
    const qEl = document.getElementById('q-text');
    const opts = document.getElementById('opts');
    const nextBtn = document.getElementById('next-btn');
    const statAnswered = document.getElementById('stat-answered');
    const statMatches = document.getElementById('stat-matches');
    const statPercent = document.getElementById('stat-percent');
    const loader = document.getElementById('loading-indicator');
    const errorDisp = document.getElementById('error-display');
    const progressIndicator = document.getElementById('batch-progress');
    const waitingIndicator = document.getElementById('waiting-indicator');
    const newBatchBtn = document.getElementById('new-batch-btn');
    const quizComplete = document.getElementById('quiz-complete');
    const completeScore = document.getElementById('complete-score');
    const completeMatches = document.getElementById('complete-matches');
    const completeTotalQs = document.getElementById('complete-total-qs');
    const batchResultsContainer = document.getElementById('batch-results');

    // State variables
    let answered = 0;
    let matches = 0;
    let currentQ = null;
    let currentBatchId = null;
    let batchSize = 5;
    let batchProgress = 0;
    let pollInterval = null;

    // Function to update all score displays
    function updateScoreDisplays(score, matchPercent) {
        // Update main score
        if (score !== undefined && score !== null) {
            scoreEl.textContent = score;
        }

        // Update score percent in header
        const scorePercentEl = document.getElementById('score-percent');
        if (scorePercentEl && matchPercent !== undefined && matchPercent !== null) {
            scorePercentEl.textContent = `${matchPercent}%`;
        }

        // Update stats
        if (matchPercent !== undefined && matchPercent !== null) {
            statPercent.textContent = `${matchPercent}%`;
        }
    }

    // Fetch helper for API calls
    async function fetchAPI(endpoint, options = {}) {
        const url = `/api/quiz/${endpoint}`;

        try {
            const response = await fetch(url, options);

            if (response.status === 401) {
                // Session expired, redirect to login
                window.location = '/login';
                return null;
            }

            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API error (${endpoint}):`, error);
            throw error;
        }
    }

    // Legacy API call for backward compatibility
    async function legacyFetchAPI(endpoint, options = {}) {
        try {
            const response = await fetch(`/api/quiz/${endpoint}`, options);

            if (response.status === 401) {
                window.location = '/login';
                return null;
            }

            return await response.json();
        } catch (error) {
            console.error(`Legacy API error (${endpoint}):`, error);
            throw error;
        }
    }

    // Load the overall score and stats
    async function loadStats() {
        try {
            let data;

            try {
                // Try new API first
                data = await fetchAPI('score');
            } catch (e) {
                // Fall back to legacy API
                console.log('Falling back to legacy score API');
                data = await legacyFetchAPI('score');
            }

            if (!data) return;

            scoreEl.textContent = data.score || 0;
            statAnswered.textContent = data.total_answered || 0;
            statMatches.textContent = data.matches || 0;

            // Calculate percentage
            const matchPercent = data.match_percent || (data.total_answered > 0 ? Math.round((data.matches / data.total_answered) * 100) : 0);

            // Update all percentages
            updateScoreDisplays(data.score, matchPercent);

            // Update the stat counters
            answered = data.total_answered || 0;
            matches = data.matches || 0;
        } catch (e) {
            console.error('Error loading stats:', e);
            errorDisp.textContent = 'Error loading stats: ' + e.message;
            errorDisp.style.display = 'block';
        }
    }

    // Check quiz status
    async function checkStatus() {
        try {
            const data = await fetchAPI('status');

            if (!data) return false;

            if (!data.has_partner) {
                showPartnerRequiredMessage();
                return false;
            }

            if (data.pending_questions > 0) {
                showPendingQuestions(data.pending_questions);
            }

            if (data.has_active_batch) {
                // Continue with current batch
                if (data.batch_info && data.batch_info.completed) {
                    showBatchComplete();
                    return false;
                }
                return true;
            } else {
                // Prompt to start new batch
                showStartNewBatch();
                return false;
            }
        } catch (e) {
            console.error('Error checking status:', e);
            console.log('Status API not available, showing start new batch option');
            showStartNewBatch();
            return false;
        }
    }

    // Load or create batch
    async function loadOrCreateBatch() {
        try {
            const data = await fetchAPI('batch');

            if (!data || data.error) {
                if (data && data.error) {
                    errorDisp.textContent = data.error;
                    errorDisp.style.display = 'block';
                }
                return false;
            }

            currentBatchId = data.batch_id;
            batchSize = data.total_questions;
            batchProgress = data.current_index;

            if (data.completed) {
                showBatchComplete();
                return false;
            }

            return true;
        } catch (e) {
            console.error('Error loading batch:', e);
            errorDisp.textContent = 'Error loading batch: ' + e.message;
            errorDisp.style.display = 'block';
            return false;
        }
    }

    // Load a single question from the current batch
    async function loadQuestion() {
        errorDisp.style.display = 'none';
        loader.style.display = 'flex';
        nextBtn.style.display = 'none';
        opts.innerHTML = '';
        qEl.textContent = 'Loading question…';
        waitingIndicator.style.display = 'none';
        quizComplete.style.display = 'none';

        try {
            let data;

            try {
                // Try new batch API first
                data = await fetchAPI('question');
            } catch (e) {
                // Fall back to legacy question API
                console.log('Falling back to legacy question API');
                data = await legacyFetchAPI('question');
            }

            if (!data) {
                errorDisp.textContent = 'Could not load question data.';
                errorDisp.style.display = 'block';
                loader.style.display = 'none';
                return;
            }

            if (data.message && data.completed) {
                // Batch is complete
                showBatchComplete();
                return;
            }

            // Validate question data
            if (!data.question || !Array.isArray(data.options) || data.options.length < 2) {
                console.error('Invalid question data received:', data);
                errorDisp.textContent = 'Error: Received invalid question data from server.';
                errorDisp.style.display = 'block';
                loader.style.display = 'none';
                return;
            }

            // Make sure id exists (either from server or generate one if missing)
            if (!data.id) {
                data.id = Math.floor(Math.random() * 10000); // Generate random ID if missing
                console.log('Generated ID for question:', data.id);
            }

            // Store the current question
            currentQ = data;

            // Update progress indicator
            if (data.batch_progress) {
                batchProgress = data.batch_progress.current;
                progressIndicator.textContent = `Question ${data.batch_progress.current} of ${data.batch_progress.total}`;
                progressIndicator.style.display = 'block';
            } else {
                progressIndicator.style.display = 'none';
            }

            // Display question
            qEl.textContent = data.question;
            data.options.forEach(opt => {
                const btn = document.createElement('button');
                btn.className = 'quiz-option';
                btn.textContent = opt;
                btn.onclick = () => submitAnswer(opt);
                opts.appendChild(btn);
            });
        } catch (e) {
            console.error('Error loading question:', e);
            errorDisp.textContent = 'Error: ' + e.message;
            errorDisp.style.display = 'block';
        } finally {
            loader.style.display = 'none';
        }
    }

    // Submit your answer
    async function submitAnswer(answer) {
        // Check if currentQ is valid
        if (!currentQ || !currentQ.id) {
            console.error('Cannot submit answer: Question data is not available', currentQ);
            errorDisp.textContent = 'Error: Question data is not available. Please try refreshing the page.';
            errorDisp.style.display = 'block';
            return;
        }

        // disable choices immediately
        opts.querySelectorAll('button').forEach(b => b.disabled = true);

        try {
            let data;

            try {
                // Try new batch API first
                data = await fetchAPI('answer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question_id: currentQ.id,
                        answer: answer
                    })
                });
            } catch (e) {
                // Fall back to legacy answer API
                console.log('Falling back to legacy answer API');
                data = await legacyFetchAPI('answer', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        question_id: currentQ.id,
                        answer: answer
                    })
                });
            }

            if (!data) return;

            // Update the mini-stats
            answered++;
            if (data.is_match || data.delta > 0) matches++;
            statAnswered.textContent = answered;
            statMatches.textContent = matches;
            const matchPercent = Math.round((matches / answered) * 100);
            updateScoreDisplays(data.new_score, matchPercent);

            // Show the result banner
            const resDiv = document.createElement('div');
            const isWaiting = data.waiting_for_partner || !data.hasOwnProperty('delta');
            const isMatch = data.is_match || (data.delta && data.delta > 0);

            resDiv.className = 'answer-result ' +
                (isWaiting ? 'waiting' : (isMatch ? 'match' : 'no-match'));

            resDiv.textContent = isWaiting ?
                'Waiting for partner…' :
                (isMatch ? `Match! +${data.delta || 5}` : `No match: ${data.delta || -2}`);

            opts.appendChild(resDiv);

            // Update compatibility score if available
            if (data.new_score !== null && data.new_score !== undefined) {
                updateScoreDisplays(data.new_score, matchPercent);
            }

            if (isWaiting) {
                // Show waiting indicator
                waitingIndicator.style.display = 'block';
                nextBtn.style.display = 'none';

                // Start polling for partner response
                startPolling();
            } else {
                // Check if batch is complete
                if (data.batch_complete) {
                    setTimeout(() => showBatchComplete(), 1500);
                } else {
                    // Show next button
                    nextBtn.textContent = 'Next Question';
                    nextBtn.style.display = 'inline-block';
                }
            }
        } catch (e) {
            console.error('Error submitting answer:', e);
            errorDisp.textContent = 'Error: ' + e.message;
            errorDisp.style.display = 'block';

            // Show next button anyway so user can continue
            nextBtn.textContent = 'Next Question';
            nextBtn.style.display = 'inline-block';
        }
    }

    // Improved polling for partner response
    function startPolling() {
        // Clear any existing interval
        if (pollInterval) {
            clearInterval(pollInterval);
        }

        // Poll every 3 seconds
        pollInterval = setInterval(async() => {
            try {
                // Check if partner has answered the current question
                const responseData = await fetchAPI(`check-partner-response?question_id=${currentQ.id}`).catch(() => null);

                // If we get a valid response and partner has answered
                if (responseData && responseData.has_answered) {
                    clearInterval(pollInterval);

                    // Update UI to show match/no match result
                    const resDiv = document.createElement('div');
                    resDiv.className = `answer-result ${responseData.is_match ? 'match' : 'no-match'}`;
                    resDiv.textContent = responseData.is_match ?
                        `Match! +${responseData.delta}` :
                        `No match: ${responseData.delta}`;

                    // Replace the waiting message
                    const existingResult = document.querySelector('.answer-result');
                    if (existingResult) {
                        existingResult.replaceWith(resDiv);
                    } else {
                        opts.appendChild(resDiv);
                    }

                    // Hide waiting indicator
                    waitingIndicator.style.display = 'none';

                    // Update score
                    if (responseData.new_score !== null && responseData.new_score !== undefined) {
                        const matchPercent = Math.round((matches / answered) * 100);
                        updateScoreDisplays(responseData.new_score, matchPercent);
                    }

                    // Update stats
                    if (responseData.is_match) {
                        matches++;
                        statMatches.textContent = matches;
                        const matchPercent = Math.round((matches / answered) * 100);
                        updateScoreDisplays(null, matchPercent);
                    }

                    // Check if batch is complete
                    if (responseData.batch_complete) {
                        setTimeout(() => showBatchComplete(), 1500);
                    } else {
                        // Show next button
                        nextBtn.textContent = 'Next Question';
                        nextBtn.style.display = 'inline-block';
                    }
                }
            } catch (e) {
                console.error('Error polling for partner response:', e);
                // Don't stop polling on error
            }
        }, 3000); // Poll every 3 seconds
    }

    // Create a new batch
    async function createNewBatch() {
        errorDisp.style.display = 'none';
        loader.style.display = 'flex';
        quizComplete.style.display = 'none';
        newBatchBtn.disabled = true;

        try {
            const data = await fetchAPI('batch/new', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });

            if (!data || data.error) {
                if (data && data.error) {
                    errorDisp.textContent = data.error;
                    errorDisp.style.display = 'block';
                }
                return;
            }

            // Start the new batch
            currentBatchId = data.batch_id;
            batchSize = data.total_questions;
            batchProgress = 0;

            // Load the first question
            loadQuestion();
        } catch (e) {
            console.error('Error creating batch:', e);
            errorDisp.textContent = 'Error: ' + e.message;
            errorDisp.style.display = 'block';

            // Fallback to loading a question directly
            loadQuestion();
        } finally {
            loader.style.display = 'none';
            newBatchBtn.disabled = false;
        }
    }

    // Show messages for different states
    function showPartnerRequiredMessage() {
        opts.innerHTML = '';
        qEl.textContent = 'You need to connect with a partner to start the compatibility quiz!';
        progressIndicator.style.display = 'none';
        nextBtn.style.display = 'none';
        newBatchBtn.style.display = 'none';
    }

    function showPendingQuestions(count) {
        // Show a notification about pending questions
        const pendingNote = document.createElement('div');
        pendingNote.className = 'notification pending';
        pendingNote.textContent = `Your partner has answered ${count} question(s) that you haven't seen yet!`;
        document.querySelector('.quiz-container').prepend(pendingNote);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            pendingNote.style.opacity = '0';
            setTimeout(() => pendingNote.remove(), 500);
        }, 5000);
    }

    function showStartNewBatch() {
        opts.innerHTML = '';
        qEl.textContent = 'Ready to test your compatibility?';
        progressIndicator.style.display = 'none';
        nextBtn.style.display = 'none';
        newBatchBtn.textContent = 'Start New Question Batch';
        newBatchBtn.style.display = 'inline-block';
    }

    function showBatchComplete() {
        // Clear polling if active
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }

        // Hide question elements
        opts.innerHTML = '';
        qEl.textContent = '';
        progressIndicator.style.display = 'none';
        nextBtn.style.display = 'none';
        loader.style.display = 'none';
        waitingIndicator.style.display = 'none';

        // Show completion screen
        quizComplete.style.display = 'block';
        completeScore.textContent = scoreEl.textContent;
        completeMatches.textContent = statMatches.textContent;
        completeTotalQs.textContent = batchSize;

        // Get any batch results
        loadBatchResults();

        // Show new batch button
        newBatchBtn.textContent = 'Start New Question Batch';
        newBatchBtn.style.display = 'inline-block';
    }

    // Load results of completed batch
    async function loadBatchResults() {
        if (!currentBatchId) return;

        try {
            // Try to get results for the specific batch
            let data = await fetchAPI(`batch/${currentBatchId}/results`).catch(() => null);

            // If that endpoint doesn't exist or returns an error, create mock results
            if (!data || data.error) {
                // Create mock results based on stats
                batchResultsContainer.innerHTML = '<p>Details not available yet. Play another batch to see more!</p>';
                return;
            }

            // Display batch results
            batchResultsContainer.innerHTML = '';

            if (data.questions && data.questions.length > 0) {
                data.questions.forEach(q => {
                    const qDiv = document.createElement('div');
                    qDiv.className = `result-item ${q.match ? 'match' : 'no-match'}`;

                    qDiv.innerHTML = `
                        <div class="result-question">${q.question}</div>
                        <div class="result-answers">
                            <div class="answer">You: <strong>${q.your_answer}</strong></div>
                            <div class="answer">Partner: <strong>${q.partner_answer}</strong></div>
                        </div>
                        <div class="result-status">
                            ${q.match ? '<span class="match-icon">✓</span> Match!' : '<span class="no-match-icon">✗</span> No Match'}
                        </div>
                    `;

                    batchResultsContainer.appendChild(qDiv);
                });
            } else {
                batchResultsContainer.innerHTML = '<p>No results available for this batch yet.</p>';
            }
        } catch (e) {
            console.error('Error loading batch results:', e);
            batchResultsContainer.innerHTML = '<p>Error loading results.</p>';
        }
    }

    // Set up event handlers
    nextBtn.onclick = loadQuestion;
    newBatchBtn.onclick = createNewBatch;

    // Initialize quiz
    async function initQuiz() {
        await loadStats();

        // First try loading a question to see what API is available
        try {
            await loadQuestion();
        } catch (e) {
            console.error('Error loading initial question:', e);
            showStartNewBatch();
        }
    }

    // Start the quiz
    initQuiz();
});