const router = {
    historyStack: [],

    init() {
        window.onpopstate = (event) => {
            if (event.state && event.state.screenId) {
                this.showScreen(event.state.screenId, false);
            } else {
                this.showScreen('welcomeScreen', false);
            }
        };
        // Default
        this.showScreen('welcomeScreen', false);
    },

    goToScreen(screenId) {
        this.showScreen(screenId, true);
    },

    showScreen(screenId, pushState = true) {
        // Hide all screens
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.screen').forEach(s => s.classList.add('hidden'));

        // Show target
        const screen = document.getElementById(screenId);
        if (screen) {
            screen.classList.remove('hidden');
            screen.classList.add('active');

            // Toggle Navbars
            if (screenId === 'welcomeScreen' || screenId === 'authScreen') {
                document.getElementById('mainNavbar').classList.add('hidden');
                document.getElementById('mainSidebar').classList.add('hidden');
            } else {
                document.getElementById('mainNavbar').classList.remove('hidden');
                document.getElementById('mainSidebar').classList.remove('hidden');
            }

            if (pushState) {
                history.pushState({ screenId }, null, `#${screenId}`);
                this.historyStack.push(screenId);
            }
        }
    },

    goBack() {
        if (this.historyStack.length > 1) {
            this.historyStack.pop();
            const prev = this.historyStack[this.historyStack.length - 1];
            this.showScreen(prev, false);
            history.back();
        } else {
            this.goToScreen('welcomeScreen');
        }
    }
};
