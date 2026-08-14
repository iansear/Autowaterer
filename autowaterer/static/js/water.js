const waterButton = document.getElementById('water-button');
const waterStatus = document.getElementById('water-status');
const turnOnPumpButton = document.getElementById('turn-on-pump-button');
const turnOnPumpStatus = document.getElementById('turn-on-pump-status');
const turnOffPumpButton = document.getElementById('turn-off-pump-button');
const turnOffPumpStatus = document.getElementById('turn-off-pump-status');

waterButton.addEventListener('click', async () => {
    waterButton.disabled = true;
    waterStatus.textContent = 'Starting...';

    try {
        const response = await fetch(waterButton.dataset.waterUrl, { method: 'POST' });
        waterStatus.textContent = await response.text();
    } catch (error) {
        waterStatus.textContent = `Could not reach the server: ${error.message}`;
    } finally {
        waterButton.disabled = false;
    }
});

turnOnPumpButton.addEventListener('click', async () => {
    turnOnPumpButton.disabled = true;
    turnOnPumpStatus.textContent = 'Starting...';

    try {
        const response = await fetch(turnOnPumpButton.dataset.turnOnPumpUrl, { method: 'POST' });
        turnOnPumpStatus.textContent = await response.text();
    } catch (error) {
        turnOnPumpStatus.textContent = `Could not reach the server: ${error.message}`;
    } finally {
        turnOnPumpButton.disabled = false;
    }
});

turnOffPumpButton.addEventListener('click', async () => {
    turnOffPumpButton.disabled = true;
    turnOffPumpStatus.textContent = 'Starting...';

    try {
        const response = await fetch(turnOffPumpButton.dataset.turnOffPumpUrl, { method: 'POST' });
        turnOffPumpStatus.textContent = await response.text();
    } catch (error) {
        turnOffPumpStatus.textContent = `Could not reach the server: ${error.message}`;
    } finally {
        turnOffPumpButton.disabled = false;
    }
});