const router = {
    screens: [
        'authScreen', 'dashboardScreen', 'academyScreen', 'arcadeScreen',
        'arenaScreen', 'coachScreen', 'profileScreen', 'hallOfFameScreen', 'settingsScreen'
    ],

    init() {
        window.onpopstate = (event) => {
            if (event.state && event.state.screen) {
                this.showScreen(event.state.screen, false);
            }
        };

        // Default route
        if (!location.hash) {
            this.goToScreen('dashboardScreen');
        } else {
            const screen = location.hash.substring(1);
            if (this.screens.includes(screen)) {
                this.goToScreen(screen);
            }
        }
    },

    goToScreen(screenId) {
        this.showScreen(screenId, true);
    },

    showScreen(screenId, pushState = true) {
        // Hide all screens
        this.screens.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.classList.add('hidden');
        });

        // Show target screen
        const target = document.getElementById(screenId);
        if (target) {
            target.classList.remove('hidden');

            // Update Sidebar Active State
            document.querySelectorAll('.nav-item').forEach(item => {
                item.classList.remove('active');
                if (item.getAttribute('onclick') && item.getAttribute('onclick').includes(screenId)) {
                    item.classList.add('active');
                }
            });

            if (pushState) {
                history.pushState({ screen: screenId }, null, `#${screenId}`);
            }
        }
    }
};
