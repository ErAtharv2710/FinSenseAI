const profile = {
    init() {
        this.loadProfile();
    },

    loadProfile() {
        const user = JSON.parse(localStorage.getItem('authUser'));
        const stats = utils.getUserStats();

        if (user) {
            const nameEl = document.querySelector('.profile-card h3');
            if (nameEl) nameEl.textContent = user.name;

            const statsEl = document.querySelector('.profile-card p.text-muted');
            if (statsEl) statsEl.textContent = `Level ${stats.level} • ${stats.xp} XP`;
        }
    },

    editProfile() {
        const user = JSON.parse(localStorage.getItem('authUser'));
        const newName = prompt("Enter new name:", user.name);
        if (newName) {
            user.name = newName;
            localStorage.setItem('authUser', JSON.stringify(user));
            this.loadProfile();
            // Update Navbar too
            document.getElementById('nav-avatar').src = `https://ui-avatars.com/api/?name=${newName}&background=00C853&color=fff`;
        }
    },

    deleteAccount() {
        if (confirm('Are you sure you want to delete your account? This cannot be undone.')) {
            localStorage.clear();
            location.reload();
        }
    }
};
