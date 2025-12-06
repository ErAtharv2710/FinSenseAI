const utils = {
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    },

    showToast(message, type = 'info') {
        alert(`${type.toUpperCase()}: ${message}`); // Simple alert for now, can upgrade to custom toast
    },

    getUserStats() {
        const stats = localStorage.getItem('userStats');
        return stats ? JSON.parse(stats) : { level: 1, xp: 0, net_worth: 0 };
    },

    saveUserStats(stats) {
        localStorage.setItem('userStats', JSON.stringify(stats));
    }
};
