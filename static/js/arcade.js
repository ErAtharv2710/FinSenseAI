const arcade = {
    playGame(game) {
        document.getElementById('game-container').classList.remove('hidden');
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#0B1020';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#00C853';
        ctx.font = '30px Inter';
        ctx.fillText(`Playing ${game.toUpperCase()}...`, 50, 50);
    },

    closeGame() {
        document.getElementById('game-container').classList.add('hidden');
    }
};
