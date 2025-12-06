const academy = {
    tracks: [
        { id: 'budgeting', title: 'Budgeting 101', progress: 0 },
        { id: 'credit', title: 'Credit Scores', progress: 0 },
        { id: 'investing', title: 'Investing Basics', progress: 0 }
    ],

    init() {
        this.renderTracks();
    },

    renderTracks() {
        const container = document.querySelector('#academyScreen .glass-card');
        let html = '<div class="track-list">';

        this.tracks.forEach(track => {
            html += `
                <div class="track-item" style="background:rgba(255,255,255,0.05); padding:1rem; margin-bottom:1rem; border-radius:12px; cursor:pointer;" onclick="academy.startTrack('${track.id}')">
                    <div style="display:flex; justify-content:space-between;">
                        <h4>${track.title}</h4>
                        <span>${track.progress}%</span>
                    </div>
                    <div style="height:4px; background:#333; margin-top:0.5rem; border-radius:2px;">
                        <div style="width:${track.progress}%; height:100%; background:var(--primary);"></div>
                    </div>
                </div>
            `;
        });
        html += '</div>';
        container.innerHTML = html;
    },

    async startTrack(trackId) {
        // For now, just launch a quiz
        const container = document.querySelector('#academyScreen .glass-card');
        container.innerHTML = `<h3>Quiz: ${trackId.toUpperCase()}</h3><div id="quiz-area">Loading questions...</div>`;

        try {
            const res = await fetch(`/api/academy/quiz?track=${trackId}`);
            const data = await res.json();
            this.renderQuiz(data.questions);
        } catch (e) {
            container.innerHTML = 'Error loading quiz.';
        }
    },

    renderQuiz(questions) {
        const area = document.getElementById('quiz-area');
        let html = '';
        questions.forEach((q, idx) => {
            html += `
                <div class="quiz-q mb-4">
                    <p><strong>Q${idx + 1}:</strong> ${q.question}</p>
                    <div class="options">
                        ${q.options.map((opt, i) => `
                            <button class="btn btn-outline mb-2" style="width:100%; text-align:left;" onclick="academy.checkAnswer(this, ${i}, ${q.correct})">${opt}</button>
                        `).join('')}
                    </div>
                </div>
            `;
        });
        area.innerHTML = html;
    },

    checkAnswer(btn, selected, correct) {
        if (selected === correct) {
            btn.style.borderColor = 'var(--primary)';
            btn.style.background = 'rgba(0, 200, 83, 0.2)';
            utils.showToast('Correct! +10 XP', 'success');
        } else {
            btn.style.borderColor = '#EF4444';
            btn.style.background = 'rgba(239, 68, 68, 0.2)';
            utils.showToast('Try again!', 'error');
        }
    }
};
