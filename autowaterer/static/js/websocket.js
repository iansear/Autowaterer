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
            const statusIndicator = document.querySelector(
                `.pump-status-indicator[data-pump-id="${status.id}"]`
            );
            if (statusIndicator) {
                statusIndicator.style.background = status.running ? 'green' : 'red';
            }
            const elapsed = document.querySelector(
                `.pump-elapsed[data-pump-id="${status.id}"]`
            );
            if (elapsed) {
                elapsed.textContent = `${status.elapsed}s`;
            }
            const lastRun = document.querySelector(
                `.pump-last-run[data-pump-id="${status.id}"]`
            );
            if (lastRun) {
                lastRun.textContent = status.last_run;
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
