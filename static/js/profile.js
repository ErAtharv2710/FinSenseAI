const profile = {
    startDeleteFlow() {
        document.getElementById('delete-modal').classList.remove('hidden');
    },

    cancelDelete() {
        document.getElementById('delete-modal').classList.add('hidden');
    },

    async confirmDelete() {
        if (confirm("Are you absolutely sure? This cannot be undone.")) {
            try {
                const user = firebase.auth().currentUser;
                await user.delete();
                utils.showToast('Account deleted.', 'success');
                this.cancelDelete();
            } catch (error) {
                utils.showToast(error.message, 'error');
            }
        }
    }
};
