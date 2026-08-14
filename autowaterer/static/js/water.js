const waterStatus = document.getElementById('water-status');

function postOnClick(buttonId, urlAttribute) {
    const button = document.getElementById(buttonId);
    if (!button) {
        return;
    }

    button.addEventListener('click', async () => {
        button.disabled = true;
        waterStatus.textContent = 'Working...';

        try {
            const response = await fetch(button.dataset[urlAttribute], { method: 'POST' });
            waterStatus.textContent = await response.text();
        } catch (error) {
            waterStatus.textContent = `Could not reach the server: ${error.message}`;
        } finally {
            button.disabled = false;
        }
    });
}

postOnClick('water-button', 'waterUrl');
postOnClick('turn-on-pump-button', 'turnOnPumpUrl');
postOnClick('turn-off-pump-button', 'turnOffPumpUrl');
