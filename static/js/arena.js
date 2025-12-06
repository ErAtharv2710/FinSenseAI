const arena = {
    currentRoom: null,

    async createRoom() {
        if (!auth.user) return utils.showToast('Login required', 'error');

        const roomCode = Math.random().toString(36).substring(2, 8).toUpperCase();
        const roomRef = db.collection('rooms').doc(roomCode);

        await roomRef.set({
            host: auth.user.uid,
            players: [{ uid: auth.user.uid, name: auth.user.displayName || 'Host', score: 0 }],
            status: 'waiting',
            created_at: new Date().toISOString()
        });

        this.joinRoomLogic(roomCode);
    },

    async joinRoom() {
        const code = document.getElementById('room-code').value.toUpperCase();
        if (!code) return;

        const roomRef = db.collection('rooms').doc(code);
        const doc = await roomRef.get();

        if (doc.exists) {
            // Add player
            const roomData = doc.data();
            const newPlayer = { uid: auth.user.uid, name: auth.user.displayName || 'Player', score: 0 };

            // Avoid duplicates
            if (!roomData.players.find(p => p.uid === auth.user.uid)) {
                roomData.players.push(newPlayer);
                await roomRef.update({ players: roomData.players });
            }

            this.joinRoomLogic(code);
        } else {
            utils.showToast('Room not found', 'error');
        }
    },

    joinRoomLogic(code) {
        this.currentRoom = code;
        document.getElementById('arena-lobby').classList.remove('hidden');

        // Real-time listener
        db.collection('rooms').doc(code).onSnapshot(doc => {
            const data = doc.data();
            const list = document.getElementById('player-list');
            list.innerHTML = data.players.map(p => `<li>${p.name} - ${p.score} pts</li>`).join('');
        });
    }
};
