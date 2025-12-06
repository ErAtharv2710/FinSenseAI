const profile = {
    init() {
        this.loadProfile();
    },

    loadProfile() {
        const user = JSON.parse(localStorage.getItem('authUser'));
        const userProfile = JSON.parse(localStorage.getItem('userProfile')) || {};
        const stats = utils.getUserStats();

        if (user) {
            // Header
            const nameEl = document.querySelector('.profile-card h3');
            if (nameEl) nameEl.textContent = userProfile.username || user.name;

            const statsEl = document.querySelector('.profile-card p.text-muted');
            if (statsEl) statsEl.textContent = `Level ${stats.level} • ${stats.xp} XP`;

            // Details Section (if exists)
            const detailsContainer = document.getElementById('profile-details');
            if (detailsContainer) {
                detailsContainer.innerHTML = `
                    <div class="profile-detail-row">
                        <span><i class="fas fa-map-marker-alt text-accent"></i> City</span>
                        <span>${userProfile.city || 'Not Set'}</span>
                    </div>
                    <div class="profile-detail-row">
                        <span><i class="fas fa-briefcase text-primary"></i> Employment</span>
                        <span>${userProfile.employment_status || 'Not Set'}</span>
                    </div>
                    <div class="profile-detail-row">
                        <span><i class="fas fa-rupee-sign text-success"></i> Monthly Income</span>
                        <span>₹${userProfile.monthly_income || 0}</span>
                    </div>
                    <div class="profile-detail-row">
                        <span><i class="fas fa-chart-line text-warning"></i> Risk Tolerance</span>
                        <span>${userProfile.risk_tolerance || 'Moderate'}</span>
                    </div>
                `;
            }
        }
    },

    editProfile() {
        const userProfile = JSON.parse(localStorage.getItem('userProfile')) || {};

        // Simple Prompt-based editing for now (can be upgraded to a modal)
        const newName = prompt("Enter Name:", userProfile.username || "");
        if (newName === null) return;

        const newCity = prompt("Enter City:", userProfile.city || "");
        if (newCity === null) return;

        const newEmployment = prompt("Employment Status (student/employed/unemployed):", userProfile.employment_status || "student");
        if (newEmployment === null) return;

        const newIncome = prompt("Monthly Income (INR):", userProfile.monthly_income || 0);
        if (newIncome === null) return;

        // Update Object
        userProfile.username = newName;
        userProfile.city = newCity;
        userProfile.employment_status = newEmployment;
        userProfile.monthly_income = parseInt(newIncome);

        // Save
        localStorage.setItem('userProfile', JSON.stringify(userProfile));

        // Update Auth User too for consistency
        const authUser = JSON.parse(localStorage.getItem('authUser'));
        authUser.name = newName;
        localStorage.setItem('authUser', JSON.stringify(authUser));

        // Reload UI
        this.loadProfile();
        document.getElementById('nav-avatar').src = `https://ui-avatars.com/api/?name=${newName}&background=00C853&color=fff`;
    },

    deleteAccount() {
        if (confirm('Are you sure you want to delete your account? This cannot be undone.')) {
            localStorage.clear();
            location.reload();
        }
    }
};
