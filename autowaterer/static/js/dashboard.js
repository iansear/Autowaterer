// Web Socket
const statusContainer = document.getElementById('status-container');
const statusTexts = document.querySelectorAll('.pump-status');

function pumpStatusSocketUrl() {
    return statusContainer.dataset.pumpStatusUrl;
}

function connectPumpStatus() {
    if (!statusContainer || !statusTexts) {
        return;
    }

    const socket = new WebSocket(pumpStatusSocketUrl());

    socket.onopen = () => {
        statusText.textContent = 'Connected.';
    };

    socket.onmessage = (event) => {
        const statuses = JSON.parse(event.data);
        statuses.forEach(status => {
            const statusText = document.querySelector(`[data-pump-id="${status.id}"]`);
            if (status.running) {
                statusText.textContent = `ON — ${status.elapsed}s`;
            } else {
                statusText.textContent = 'OFF';
            }
        });
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