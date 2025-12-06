const auth = {
    user: null,

    init() {
        authObj.onAuthStateChanged(user => {
            if (user) {
                this.user = user;
                this.updateUI(user);
                // Hide auth, show dashboard
                document.getElementById('authScreen').classList.add('hidden');
                document.getElementById('navbar').classList.remove('hidden');
                document.getElementById('sidebar').classList.remove('hidden');

                // If we are on auth screen, go to dashboard
                if (!location.hash || location.hash === '#authScreen') {
                    router.goToScreen('dashboardScreen');
                }
            } else {
                this.user = null;
                document.getElementById('authScreen').classList.remove('hidden');
                document.getElementById('navbar').classList.add('hidden');
                document.getElementById('sidebar').classList.add('hidden');
            }
        });
    },

    updateUI(user) {
        document.getElementById('nav-username').textContent = user.displayName || 'User';
        document.getElementById('nav-avatar').src = `https://ui-avatars.com/api/?name=${user.displayName || 'User'}&background=00C853&color=fff`;

        // Profile Screen Updates
        document.getElementById('prof-display-name').textContent = user.displayName || 'User';
        document.getElementById('prof-email').textContent = user.email;
        document.getElementById('prof-avatar').src = `https://ui-avatars.com/api/?name=${user.displayName || 'User'}&background=00C853&color=fff`;
    },

    switchTab(tab) {
        document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
        document.getElementById(`tab-${tab}`).classList.add('active');

        if (tab === 'signin') {
            document.getElementById('signinForm').classList.remove('hidden');
            document.getElementById('signupForm').classList.add('hidden');
        } else {
            document.getElementById('signinForm').classList.add('hidden');
            document.getElementById('signupForm').classList.remove('hidden');
        }
    },

    toggleLoginOTP() {
        const row = document.getElementById('login-otp-row');
        row.classList.toggle('hidden');
    },

    async handleSignIn(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        try {
            await authObj.signInWithEmailAndPassword(email, password);
            utils.showToast('Welcome back!', 'success');
        } catch (error) {
            utils.showToast(error.message, 'error');
        }
    },

    async handleSignUp(e) {
        e.preventDefault();
        const name = document.getElementById('reg-name').value;
        const display = document.getElementById('reg-display').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        const confirm = document.getElementById('reg-confirm').value;

        if (password !== confirm) return utils.showToast('Passwords do not match', 'error');

        try {
            const cred = await authObj.createUserWithEmailAndPassword(email, password);
            await cred.user.updateProfile({ displayName: display });

            // Create Firestore Profile
            await db.collection('users').doc(cred.user.uid).set({
                uid: cred.user.uid,
                username: display,
                fullName: name,
                email: email,
                created_at: new Date().toISOString(),
                financial_literacy_level: 'beginner',
                level: 1,
                xp: 0
            });

            utils.showToast('Account created!', 'success');
        } catch (error) {
            utils.showToast(error.message, 'error');
        }
    },

    logout() {
        authObj.signOut();
    }
};
