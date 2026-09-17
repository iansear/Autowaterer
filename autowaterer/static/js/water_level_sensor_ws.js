const statusContainer = document.getElementById('water-level-status-container');
const statusText = document.getElementById('water-level-status-text');

function connectWaterLevelStatus() {
    if (!statusContainer || !statusText) {
        return;
    }

    const socket = new WebSocket(statusContainer.dataset.waterLevelStatusUrl);

    socket.onopen = () => {
        statusText.textContent = 'Connected.';
    };

    socket.onmessage = (event) => {
        const statuses = JSON.parse(event.data);
        statuses.forEach((status) => {
            const waterLevelHeight = document.querySelector(
                `.water-level-height[data-water-level-sensor-id="${status.id}"]`
            );
            if (waterLevelHeight) {
                waterLevelHeight.textContent =
                    status.water_height == null ? '—' : `${status.water_height} cm`;
            }
            const waterLevelPercentage = document.querySelector(
                `.water-level-percentage[data-water-level-sensor-id="${status.id}"]`
            );
            if (waterLevelPercentage) {
                waterLevelPercentage.textContent =
                    status.water_level_percentage == null
                        ? '—'
                        : `${status.water_level_percentage}%`;
            }
        });
    };

    socket.onclose = () => {
        statusText.textContent = 'Disconnected. Reconnecting...';
        setTimeout(connectWaterLevelStatus, 2000);
    };

    socket.onerror = () => {
        statusText.textContent = 'Error. Reconnecting...';
        socket.close();
    };
}

connectWaterLevelStatus();
