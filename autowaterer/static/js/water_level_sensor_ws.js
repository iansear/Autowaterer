const waterLevelStatusContainer = document.getElementById('water-level-status-container');
const waterLevelStatusText = document.getElementById('water-level-status-text');

function connectWaterLevelStatus() {
    if (!waterLevelStatusContainer || !waterLevelStatusText) {
        return;
    }

    const socket = new WebSocket(waterLevelStatusContainer.dataset.waterLevelStatusUrl);

    socket.onopen = () => {
        waterLevelStatusText.textContent = 'Connected.';
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
        waterLevelStatusText.textContent = 'Disconnected. Reconnecting...';
        setTimeout(connectWaterLevelStatus, 2000);
    };

    socket.onerror = () => {
        waterLevelStatusText.textContent = 'Error. Reconnecting...';
        socket.close();
    };
}

connectWaterLevelStatus();
