const auth = {
    init() {
        // Check Persistence
        const user = localStorage.getItem('authUser');
        if (user) {
            console.log('User restored:', JSON.parse(user));
            if (location.hash === '' || location.hash === '#welcomeScreen' || location.hash === '#authScreen') {
                router.goToScreen('dashboardScreen');
            }
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
        const email = document.getElementById('login-email').value;
        // Mock Auth
        const user = { email: email, name: email.split('@')[0] };
        localStorage.setItem('authUser', JSON.stringify(user));

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
        const name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;

        console.log('Creating Account for:', name);

        // 1. Create User Object
        const user = {
            email: email,
            name: name,
            uid: 'user_' + Math.random().toString(36).substr(2, 9)
        };

        // 2. Create Firestore Profile (Mocked here, but structure is ready)
        const userProfile = {
            username: name,
            email: email,
            level: 1,
            xp: 0,
            net_worth: 0,
            budget_limit: { food: 5000, entertainment: 2000, savings: 1000 },
            spending_log: [],
            joined_at: new Date().toISOString()
        };

        // In real Firebase: db.collection('users').doc(user.uid).set(userProfile)
        console.log('Firestore Profile Created:', userProfile);
        localStorage.setItem('userProfile', JSON.stringify(userProfile)); // Simulate DB

        // 3. Login
        localStorage.setItem('authUser', JSON.stringify(user));
        utils.saveUserStats({ xp: 0, level: 1, coins: 0 });

        dashboard.loadPersonalizedDashboard();
        router.goToScreen('dashboardScreen');
    },

    logout() {
        localStorage.removeItem('authUser');
        router.goToScreen('welcomeScreen');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    auth.init();
});
