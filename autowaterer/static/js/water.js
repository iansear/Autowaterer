// Test Routes
const waterStatus = document.getElementById('water-status');

function postOnClick(buttonId, urlAttribute) {
    const button = document.getElementById(buttonId);
    if (!button) {
        return;
    }

    button.addEventListener('click', async () => {
        button.disabled = true;
        waterStatus.textContent = 'Working...';

        try {
            const response = await fetch(button.dataset[urlAttribute], { method: 'POST' });
            waterStatus.textContent = await response.text();
        } catch (error) {
            waterStatus.textContent = `Could not reach the server: ${error.message}`;
        } finally {
            button.disabled = false;
        }
    });
}

postOnClick('water-button', 'waterUrl');
postOnClick('turn-on-pump-button', 'turnOnPumpUrl');
postOnClick('turn-off-pump-button', 'turnOffPumpUrl');

// Web Socket
const statusContainer = document.getElementById('status-container');
const statusText = document.getElementById('status-text');

function pumpStatusSocketUrl() {
    return statusContainer.dataset.pumpStatusUrl;
}

function connectPumpStatus() {
    if (!statusContainer || !statusText) {
        return;
    }

    const socket = new WebSocket(pumpStatusSocketUrl());

    socket.onopen = () => {
        statusText.textContent = 'Connected. Pump off.';
    };

    socket.onmessage = (event) => {
        const status = JSON.parse(event.data);
        if (status.running) {
            statusText.textContent = `ON — ${status.elapsed}s`;
        } else {
            statusText.textContent = 'OFF';
        }
    };

    socket.onclose = () => {
        statusText.textContent = 'Disconnected. Reconnecting...';
        setTimeout(connectPumpStatus, 2000);
    };

    socket.onerror = () => {
        socket.close();
    };
}

connectPumpStatus();
