const profile = {
    deleteAccount() {
        if (confirm('Are you sure? This cannot be undone.')) {
            alert('Account deleted.');
            router.goToScreen('welcomeScreen');
        }
    }
};
