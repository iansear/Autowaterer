const statusContainer = document.getElementById('status-container');
const statusText = document.getElementById('pump-status-text');

function pumpStatusSocketUrl() {
    return statusContainer.dataset.pumpStatusUrl;
}

function connectPumpStatus() {
    if (!statusContainer || !statusText) {
        return;
    }

    const socket = new WebSocket(pumpStatusSocketUrl());

    socket.onopen = () => {
        statusText.textContent = 'Connected.';
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
        statusText.textContent = 'Disconnected. Reconnecting...';
        setTimeout(connectPumpStatus, 2000);
    };

    socket.onerror = () => {
        statusText.textContent = 'Error. Reconnecting...';
        socket.close();
    };
}

connectPumpStatus();
