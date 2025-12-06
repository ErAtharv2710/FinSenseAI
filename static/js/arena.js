const arena = {
    currentRoom: null,

    createRoom() {
        const code = Math.random().toString(36).substring(2, 8).toUpperCase();
        console.log(`Creating room: ${code}`);

        // Mock Firebase Room Creation
        // In real app: firestore.collection('rooms').doc(code).set({...})

        this.currentRoom = { code, players: [JSON.parse(localStorage.getItem('authUser')).name] };
        this.renderRoom();
    },

    joinRoom() {
        const codeInput = document.getElementById('arena-code-input');
        const code = codeInput.value.trim().toUpperCase();
        if (!code) return alert('Please enter a room code');

        console.log(`Joining room: ${code}`);
        // Mock Join
        this.currentRoom = { code, players: ['Host', JSON.parse(localStorage.getItem('authUser')).name] };
        this.renderRoom();
    },

    renderRoom() {
        const container = document.getElementById('arena-content');
        container.innerHTML = `
            <div class="text-center">
                <h3>Room Code: <span class="text-accent">${this.currentRoom.code}</span></h3>
                <p class="text-muted">Share this code with your friends!</p>
                
                <div class="mt-4">
                    <h4>Players</h4>
                    <div class="player-list">
                        ${this.currentRoom.players.map(p => `<div class="player-tag"><i class="fas fa-user"></i> ${p}</div>`).join('')}
                    </div>
                </div>

                <div class="mt-4">
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
                <div class="form-row">
                    <input type="text" id="arena-code-input" placeholder="Room Code">
                    <button class="btn btn-primary" onclick="arena.joinRoom()">Join</button>
                    <button class="btn btn-outline" onclick="arena.createRoom()">Create New</button>
                </div>
            </div>
        `;
    }
};
