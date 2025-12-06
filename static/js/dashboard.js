const dashboard = {
    loadPersonalizedDashboard() {
        console.log('Loading dashboard...');
        // Mock Data Fetch
        document.getElementById('dash-welcome').textContent = 'Welcome back, Dipak!';

        // Fetch Coach Tip
        fetch('/api/coach/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: 'Give me a dashboard tip', mode: 'quick' })
        })
            .then(res => res.json())
            .then(data => {
                document.getElementById('dash-coach-tip').textContent = data.response;
            });
    }
};
