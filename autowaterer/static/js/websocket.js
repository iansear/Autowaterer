const statusContainer = document.getElementById('status-container');
const statusTexts = document.querySelectorAll('.pump-status');

function pumpStatusSocketUrl() {
    return statusContainer.dataset.pumpStatusUrl;
}

function connectPumpStatus() {
    if (!statusContainer || !statusTexts.length) {
        return;
    }

    const socket = new WebSocket(pumpStatusSocketUrl());

    socket.onopen = () => {
        statusTexts.forEach((statusText) => {
            statusText.textContent = 'Connected.';
        });
    };

    socket.onmessage = (event) => {
        const statuses = JSON.parse(event.data);
        statuses.forEach((status) => {
            const statusText = document.querySelector(`.pump-status[data-pump-id="${status.id}"]`);
            if (statusText) {
                statusText.textContent = status.running ? `ON — ${status.elapsed}s` : 'OFF';
            }
            const statusIndicator = document.querySelector(
                `.pump-status-indicator[data-pump-id="${status.id}"]`
            );
            if (statusIndicator) {
                statusIndicator.style.background = status.running ? 'green' : 'red';
            }
        });
    };

    socket.onclose = () => {
        statusTexts.forEach((statusText) => {
            statusText.textContent = 'Disconnected. Reconnecting...';
        });
        setTimeout(connectPumpStatus, 2000);
    };

    socket.onerror = () => {
        socket.close();
    };
}

connectPumpStatus();
