const utils = {
    // Theme Logic
    toggleTheme() {
        const isChecked = document.getElementById('theme-toggle').checked;
        if (!isChecked) {
            document.body.classList.add('light-mode');
            localStorage.setItem('theme', 'light');
        } else {
            document.body.classList.remove('light-mode');
            localStorage.setItem('theme', 'dark');
        }
    },

    // XP & Level Logic
    getUserStats() {
        const stats = localStorage.getItem('userStats');
        return stats ? JSON.parse(stats) : { xp: 0, level: 0, coins: 0 };
    },

    saveUserStats(stats) {
        localStorage.setItem('userStats', JSON.stringify(stats));
        this.updateUI(stats);
    },

    addXP(amount) {
        let stats = this.getUserStats();
        stats.xp += amount;

        // Level Up Logic: Level = floor(XP / 100)
        const newLevel = Math.floor(stats.xp / 100);
        if (newLevel > stats.level) {
            stats.level = newLevel;
            this.showNotification(`Level Up! You are now Level ${newLevel}`, 'success');
        }

        this.saveUserStats(stats);
    },

    updateUI(stats) {
        // Update Navbar
        const xpEl = document.getElementById('nav-xp');
        if (xpEl) xpEl.textContent = `${stats.xp} XP`;

        // Update Dashboard
        const lvlEl = document.querySelector('.level-num');
        if (lvlEl) lvlEl.textContent = `Lvl ${stats.level}`;

        const profileXp = document.querySelector('.profile-card p.text-muted');
        if (profileXp) profileXp.textContent = `Level ${stats.level} • ${stats.xp} XP`;
    },

    showNotification(msg, type = 'info') {
        alert(msg); // Simple alert for now, can be upgraded to toast
    }
};
