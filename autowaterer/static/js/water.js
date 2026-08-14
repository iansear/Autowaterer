const waterButton = document.getElementById('water-button');
const turnOnPumpButton = document.getElementById('turn-on-pump-button');
const turnOffPumpButton = document.getElementById('turn-off-pump-button');
const waterStatus = document.getElementById('water-status');

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
    waterStatus.textContent = 'Starting...';

    try {
        const response = await fetch(turnOnPumpButton.dataset.turnOnPumpUrl, { method: 'POST' });
        waterStatus.textContent = await response.text();
    } catch (error) {
        waterStatus.textContent = `Could not reach the server: ${error.message}`;
    } finally {
        turnOnPumpButton.disabled = false;
    }
});

turnOffPumpButton.addEventListener('click', async () => {
    turnOffPumpButton.disabled = true;
    waterStatus.textContent = 'Starting...';

    try {
        const response = await fetch(turnOffPumpButton.dataset.turnOffPumpUrl, { method: 'POST' });
        waterStatus.textContent = await response.text();
    } catch (error) {
        waterStatus.textContent = `Could not reach the server: ${error.message}`;
    } finally {
        turnOffPumpButton.disabled = false;
    }
});
