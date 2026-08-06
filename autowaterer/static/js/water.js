const waterButton = document.getElementById('water-button');
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
