const coach = {
    async sendMessage() {
        const input = document.getElementById('coach-input');
        const msg = input.value.trim();
        if (!msg) return;

        // UI Update
        this.appendMessage(msg, 'user-msg');
        input.value = '';

        // API Call
        try {
            const res = await fetch('/api/coach/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg, mode: 'quick' })
            });
            const data = await res.json();
            this.appendMessage(data.response, 'coach-msg');
        } catch (e) {
            this.appendMessage("Sorry, I'm having trouble connecting.", 'coach-msg');
        }
    },

    appendMessage(text, className) {
        const history = document.getElementById('chat-history');
        const div = document.createElement('div');
        div.className = `msg ${className}`;
        div.textContent = text;
        div.style.marginBottom = '1rem';
        div.style.padding = '0.8rem';
        div.style.borderRadius = '12px';
        div.style.maxWidth = '80%';

        if (className === 'user-msg') {
            div.style.background = 'var(--primary)';
            div.style.color = '#000';
            div.style.alignSelf = 'flex-end';
            div.style.marginLeft = 'auto';
        } else {
            div.style.background = 'rgba(255,255,255,0.1)';
            div.style.color = '#fff';
        }

        history.appendChild(div);
        history.scrollTop = history.scrollHeight;
    }
};
