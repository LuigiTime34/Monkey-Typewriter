function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

function formatDateTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function generateRandomChar() {
    return String.fromCharCode(32 + Math.floor(Math.random() * 95));
}

let randomCharInterval;
let lastCompletionState = false;

function updateSimulation() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('status').textContent = data.running ? 'Running' : 'Stopped';
            document.getElementById('mode').textContent = data.mode || 'None';
            
            const elapsed = Math.floor(data.elapsed_seconds);
            document.getElementById('time-elapsed').textContent = formatTime(elapsed);
            
            document.getElementById('progress').textContent = 
                `${data.progress.line}/${data.progress.total_lines}`;
            
            document.getElementById('target-text').textContent = data.target_text;
            
            document.getElementById('context-lines').textContent = 
                data.context_lines.join('\n');
            
            document.getElementById('current-line').textContent = data.current_line;

            // Handle completion status
            if (data.is_completed && !lastCompletionState) {
                const completionDiv = document.getElementById('completion-status');
                completionDiv.classList.remove('hidden');
                
                document.getElementById('completion-time').textContent = 
                    formatDateTime(data.time_completed);
                document.getElementById('total-time').textContent = 
                    formatTime(data.completion_seconds);
                document.getElementById('final-attempts').textContent = 
                    data.total_attempts.toLocaleString();
                document.getElementById('final-chars').textContent = 
                    data.total_correct_chars.toLocaleString();
                document.getElementById('final-avg-attempts').textContent = 
                    (data.total_attempts / data.total_correct_chars).toFixed(2);
            }
            lastCompletionState = data.is_completed;

            if (data.running) {
                if (!randomCharInterval) {
                    randomCharInterval = setInterval(() => {
                        document.getElementById('random-char').textContent = generateRandomChar();
                    }, 50);
                }
            } else if (randomCharInterval) {
                clearInterval(randomCharInterval);
                randomCharInterval = null;
                document.getElementById('random-char').textContent = '';
            }

            document.getElementById('total-attempts').textContent = data.total_attempts.toLocaleString();
            const avgAttempts = data.total_correct_chars > 0 
                ? (data.total_attempts / data.total_correct_chars).toFixed(2)
                : '0.00';
            document.getElementById('avg-attempts').textContent = avgAttempts;
        });
}

setInterval(updateSimulation, 100);