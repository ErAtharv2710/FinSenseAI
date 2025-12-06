const auth = {
    init() {
        // Check Persistence
        const user = localStorage.getItem('authUser');
        if (user) {
            console.log('User restored:', JSON.parse(user));
            // Auto-redirect if on welcome/auth screen
            if (location.hash === '' || location.hash === '#welcomeScreen' || location.hash === '#authScreen') {
                router.goToScreen('dashboardScreen');
            }
            // Load stats
            const stats = utils.getUserStats();
            utils.updateUI(stats);
        }
    },

    openSignInForm() {
        router.goToScreen('authScreen');
        this.switchTab('signin');
    },

    openCreateAccountForm() {
        router.goToScreen('authScreen');
        this.switchTab('signup');
    },

    switchTab(tab) {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.auth-form').forEach(f => {
            f.classList.remove('active');
            f.classList.add('hidden');
        });

        document.getElementById(`tab-${tab}`).classList.add('active');
        document.getElementById(`${tab}Form`).classList.remove('hidden');
        document.getElementById(`${tab}Form`).classList.add('active');
    },

    toggleOtpLogin() {
        document.getElementById('otp-login-row').classList.toggle('hidden');
    },

    handleSignIn(e) {
        e.preventDefault();
        console.log('Signing in...');

        // Mock Auth
        const user = { email: 'user@example.com', name: 'Test User' };
        localStorage.setItem('authUser', JSON.stringify(user));

        // Initialize Stats if new
        if (!localStorage.getItem('userStats')) {
            utils.saveUserStats({ xp: 0, level: 0, coins: 0 });
        } else {
            utils.updateUI(utils.getUserStats());
        }

        dashboard.loadPersonalizedDashboard();
        router.goToScreen('dashboardScreen');
    },

    handleSignUp(e) {
        e.preventDefault();
        console.log('Signing up...');

        const user = { email: 'new@example.com', name: 'New User' };
        localStorage.setItem('authUser', JSON.stringify(user));
        utils.saveUserStats({ xp: 0, level: 0, coins: 0 });

        dashboard.loadPersonalizedDashboard();
        router.goToScreen('dashboardScreen');
    },

    logout() {
        localStorage.removeItem('authUser');
        router.goToScreen('welcomeScreen');
    }
};

// Init Auth on Load
document.addEventListener('DOMContentLoaded', () => {
    auth.init();
});
