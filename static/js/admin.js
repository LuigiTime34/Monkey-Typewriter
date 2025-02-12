function showMessage(message, isError = false) {
    const statusDiv = document.getElementById('status-message');
    statusDiv.textContent = message;
    statusDiv.className = `mt-4 p-4 rounded ${isError ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
    statusDiv.classList.remove('hidden');
    setTimeout(() => {
        statusDiv.classList.add('hidden');
    }, 3000);
}

document.getElementById('file-upload').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('target-text').value = e.target.result;
        showMessage('File loaded successfully');
    };
    reader.onerror = function(e) {
        showMessage('Error reading file', true);
    };
    reader.readAsText(file);
});

function startSimulation(mode) {
    const text = document.getElementById('target-text').value;
    if (!text.trim()) {
        showMessage('Please enter some text to simulate', true);
        return;
    }
    
    fetch('/api/start', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            mode: mode
        })
    })
    .then(response => response.json())
    .then(data => {
        showMessage(`Simulation started in ${mode} mode`);
    })
    .catch(error => {
        showMessage('Error starting simulation', true);
    });
}

function stopSimulation() {
    fetch('/api/stop', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        showMessage('Simulation stopped');
    })
    .catch(error => {
        showMessage('Error stopping simulation', true);
    });
}