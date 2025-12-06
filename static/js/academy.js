const academy = {
    currentQuestions: [],
    currentQuestionIndex: 0,
    score: 0,

    selectTrack(trackId) {
        document.querySelectorAll('.track-card').forEach(c => c.classList.remove('active'));
        event.currentTarget.classList.add('active');
        document.getElementById('track-title').textContent = trackId.charAt(0).toUpperCase() + trackId.slice(1) + ' 101';
        document.getElementById('quiz-area').classList.add('hidden');
    },

    startLesson() {
        alert('Starting lesson content...');
    },

    startQuiz() {
        fetch('/api/academy/quiz')
            .then(res => res.json())
            .then(data => {
                this.currentQuestions = data.questions;
                this.currentQuestionIndex = 0;
                this.score = 0;
                this.renderQuiz();
            });
    },

    renderQuiz() {
        const quizArea = document.getElementById('quiz-area');
        quizArea.classList.remove('hidden');

        if (this.currentQuestionIndex >= this.currentQuestions.length) {
            this.finishQuiz();
            return;
        }

        const q = this.currentQuestions[this.currentQuestionIndex];
        document.getElementById('quiz-q-text').textContent = `${this.currentQuestionIndex + 1}. ${q.question}`;

        const optionsContainer = document.getElementById('quiz-options');
        optionsContainer.innerHTML = '';

        q.options.forEach((opt, idx) => {
            const div = document.createElement('div');
            div.className = 'quiz-option';
            div.textContent = opt;
            div.onclick = () => this.selectOption(idx, q.correct, div);
            optionsContainer.appendChild(div);
        });
    },

    selectOption(selectedIdx, correctIdx, element) {
        document.querySelectorAll('.quiz-option').forEach(el => el.style.pointerEvents = 'none');

        if (selectedIdx === correctIdx) {
            element.style.borderColor = '#00C853';
            element.style.backgroundColor = 'rgba(0, 200, 83, 0.2)';
            this.score++;
        } else {
            element.style.borderColor = '#EF4444';
            element.style.backgroundColor = 'rgba(239, 68, 68, 0.2)';
            // Highlight correct
            const options = document.querySelectorAll('.quiz-option');
            options[correctIdx].style.borderColor = '#00C853';
        }

        setTimeout(() => {
            this.currentQuestionIndex++;
            this.renderQuiz();
        }, 1500);
    },

    finishQuiz() {
        const xpEarned = this.score * 20; // 20 XP per correct answer
        utils.addXP(xpEarned);

        const quizArea = document.getElementById('quiz-area');
        quizArea.innerHTML = `
            <div class="text-center">
                <h3>Quiz Complete!</h3>
                <p class="text-accent" style="font-size: 2rem; margin: 1rem 0;">Score: ${this.score}/${this.currentQuestions.length}</p>
                <p class="text-primary">+${xpEarned} XP Earned</p>
                <button class="btn btn-primary" onclick="academy.closeQuiz()">Close</button>
            </div>
        `;
    },

    closeQuiz() {
        document.getElementById('quiz-area').classList.add('hidden');
        document.getElementById('quiz-area').innerHTML = `
            <div class="quiz-header"><span class="text-accent">Question</span></div>
            <p class="quiz-question" id="quiz-q-text"></p>
            <div class="quiz-options" id="quiz-options"></div>
        `;
    }
};
