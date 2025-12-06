const arcade = {
    gameLoop: null,
    canvas: null,
    ctx: null,
    score: 0,
    playerY: 200,
    obstacles: [],

    startSavingsSprint() {
        this.canvas = document.getElementById('gameCanvas');
        this.canvas.classList.remove('hidden');
        this.ctx = this.canvas.getContext('2d');
        this.score = 0;
        this.obstacles = [];
        this.playerY = 300;

        if (this.gameLoop) clearInterval(this.gameLoop);
        this.gameLoop = setInterval(() => this.update(), 20);

        // Input
        window.addEventListener('keydown', (e) => {
            if (e.code === 'Space' && this.playerY > 200) this.playerY -= 100;
        });
    },

    update() {
        // Clear
        this.ctx.fillStyle = '#0B1020';
        this.ctx.fillRect(0, 0, 800, 400);

        // Ground
        this.ctx.fillStyle = '#00C853';
        this.ctx.fillRect(0, 350, 800, 50);

        // Player
        this.ctx.fillStyle = '#FFC107';
        this.ctx.fillRect(100, this.playerY, 30, 30);

        // Gravity
        if (this.playerY < 320) this.playerY += 5;

        // Obstacles
        if (Math.random() < 0.02) {
            this.obstacles.push({ x: 800, type: 'expense' });
        }

        this.obstacles.forEach((obs, idx) => {
            obs.x -= 5;
            this.ctx.fillStyle = '#EF4444';
            this.ctx.fillRect(obs.x, 320, 30, 30);

            // Collision
            if (obs.x < 130 && obs.x > 70 && this.playerY > 290) {
                this.gameOver();
            }
        });

        // Score
        this.score++;
        this.ctx.fillStyle = '#FFF';
        this.ctx.font = '20px Inter';
        this.ctx.fillText(`Savings: $${this.score}`, 20, 30);
    },

    gameOver() {
        clearInterval(this.gameLoop);
        alert(`Game Over! You saved $${this.score}`);
        this.canvas.classList.add('hidden');
    }
};
