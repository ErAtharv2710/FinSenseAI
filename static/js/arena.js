const arena = {
    currentRoom: null,

    createRoom() {
        // Generate Token
        const token = Math.random().toString(36).substring(2, 8).toUpperCase();
        const user = JSON.parse(localStorage.getItem('authUser'));

        console.log(`Creating room with token: ${token}`);

        // Mock Firestore Room Creation
        // db.collection('rooms').doc(token).set({ host: user.name, players: [user.name], status: 'waiting' })

        this.currentRoom = {
            token: token,
            host: user.name,
            players: [user.name]
        };
        this.renderRoom();
    },

    joinRoom() {
        const tokenInput = document.getElementById('arena-token-input');
        const token = tokenInput.value.trim().toUpperCase();
        if (!token) return alert('Please enter a room token');

        const user = JSON.parse(localStorage.getItem('authUser'));
        console.log(`Joining room: ${token}`);

        // Mock Join Logic
        // In real app: Check if doc(token) exists, then update players array

        this.currentRoom = {
            token: token,
            host: 'Friend',
            players: ['Friend', user.name]
        };
        this.renderRoom();
    },

    renderRoom() {
        const container = document.getElementById('arena-content');
        container.innerHTML = `
            <div class="text-center">
                <h3>Room Token: <span class="text-accent" style="font-size: 2rem; letter-spacing: 2px;">${this.currentRoom.token}</span></h3>
                <p class="text-muted">Share this token with your friend to join!</p>
                
                <div class="mt-4">
                    <h4>Players in Lobby</h4>
                    <div class="player-list" style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
                        ${this.currentRoom.players.map(p => `
                            <div class="player-tag" style="background: rgba(255,255,255,0.1); padding: 0.5rem 1rem; border-radius: 20px;">
                                <i class="fas fa-user"></i> ${p}
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="mt-4">
                    <button class="btn btn-primary" onclick="alert('Starting Game...')">Start Game</button>
                    <button class="btn btn-danger" onclick="arena.leaveRoom()">Leave Room</button>
                </div>
            </div>
        `;
    },

    leaveRoom() {
        this.currentRoom = null;
        // Reset UI
        document.getElementById('arena-content').innerHTML = `
            <div class="card mt-4">
                <h3>Create or Join Room</h3>
                <div class="form-row" style="display: flex; gap: 1rem; justify-content: center;">
                    <input type="text" id="arena-token-input" placeholder="Enter Token" style="padding: 0.8rem; border-radius: 8px; border: 1px solid var(--border); background: rgba(255,255,255,0.05); color: white;">
                    <button class="btn btn-primary" onclick="arena.joinRoom()">Join</button>
                    <button class="btn btn-outline" onclick="arena.createRoom()">Create New</button>
                </div>
            </div>
        `;
    }
};
