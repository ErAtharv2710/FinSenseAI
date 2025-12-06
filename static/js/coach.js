const coach = {
    currentMode: 'quick',

    setMode(mode) {
        this.currentMode = mode;
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        event.target.classList.add('active');
    },

    sendMessage() {
        const input = document.getElementById('coach-input');
        const text = input.value;
        if (!text) return;

        const win = document.getElementById('chat-window');

        // User Msg
        const userDiv = document.createElement('div');
        userDiv.className = 'msg user-msg';
        userDiv.textContent = text;
        win.appendChild(userDiv);
        input.value = '';

        // API Call
        fetch('/api/coach/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, mode: this.currentMode })
        })
            .then(res => res.json())
            .then(data => {
                const botDiv = document.createElement('div');
                botDiv.className = 'msg coach-msg';
                botDiv.textContent = data.response;
                win.appendChild(botDiv);
                win.scrollTop = win.scrollHeight;
            });
    }
};
