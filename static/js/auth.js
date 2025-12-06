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

        // 2. Create Firestore Profile with Full Schema
        const userProfile = {
            // Basic Info
            user_id: user.uid,
            username: name,
            email: email,
            created_at: new Date().toISOString(),
            last_login: new Date().toISOString(),
            is_active: true,
            profile_image_url: `https://ui-avatars.com/api/?name=${name}&background=00C853&color=fff`,
            financial_literacy_level: 'beginner', // beginner/intermediate/advanced

            // Financial Context
            currency: 'INR',
            employment_status: 'student', // student/employed/unemployed/self-employed
            monthly_income: 0,
            income_frequency: 'monthly',
            city: 'Unknown', // Requested field
            risk_tolerance: 'moderate', // conservative/moderate/aggressive

            // App Specific
            level: 1,
            xp: 0,
            net_worth: 0,
            budget_limit: { food: 5000, entertainment: 2000, savings: 1000 },

            // Sub-collections (simulated as arrays for mock)
            income_sources: [],
            expenses: [],
            savings: [],
            debts: [],
            wishlist: [],
            goals: []
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
