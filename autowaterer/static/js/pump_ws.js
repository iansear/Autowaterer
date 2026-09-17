const pumpStatusContainer = document.getElementById('pump-status-container');
const pumpStatusText = document.getElementById('pump-status-text');

function connectPumpStatus() {
    if (!pumpStatusContainer || !pumpStatusText) {
        return;
    }

    const socket = new WebSocket(pumpStatusContainer.dataset.pumpStatusUrl);

    socket.onopen = () => {
        pumpStatusText.textContent = 'Connected.';
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
        pumpStatusText.textContent = 'Disconnected. Reconnecting...';
        setTimeout(connectPumpStatus, 2000);
    };

    socket.onerror = () => {
        pumpStatusText.textContent = 'Error. Reconnecting...';
        socket.close();
    };
}

connectPumpStatus();
