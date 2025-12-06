document.addEventListener('DOMContentLoaded', () => {
    // State
    const state = {
        currentSection: 'dashboard',
    };

    // DOM Elements
    const sidebar = document.getElementById('sidebar');
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const navLinks = document.querySelectorAll('.nav-links li[data-target]');
    const contentSections = document.querySelectorAll('.content-section');
    const logoutBtn = document.getElementById('logout-btn');

    // Navigation Logic
    mobileMenuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            const targetId = link.dataset.target;
            if (targetId) {
                showSection(targetId);

                // Close sidebar on mobile
                sidebar.classList.remove('open');

                // Update active link
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            }
        });
    });

    function showSection(sectionId) {
        contentSections.forEach(sec => sec.classList.remove('active'));
        const section = document.getElementById(sectionId);
        if (section) {
            section.classList.add('active');
            state.currentSection = sectionId;
        }
    }

    // Logout
    logoutBtn.addEventListener('click', () => {
        alert('Logout logic would go here (e.g. redirect to /logout)');
    });

    // Academy Logic
    window.selectLesson = (lessonName) => {
        document.getElementById('lesson-title').textContent = lessonName;
        document.getElementById('lesson-desc').textContent = `Learn all about ${lessonName} in this interactive module.`;
        document.getElementById('start-lesson-btn').disabled = false;
        document.getElementById('quiz-area').classList.add('hidden');
    };

    document.getElementById('start-lesson-btn').addEventListener('click', () => {
        document.getElementById('quiz-area').classList.remove('hidden');
    });

    document.getElementById('submit-quiz-btn').addEventListener('click', () => {
        const selected = document.querySelector('input[name="quiz"]:checked');
        const feedback = document.getElementById('quiz-feedback');
        if (!selected) {
            feedback.textContent = 'Please select an answer.';
            feedback.style.color = 'var(--danger-color)';
            return;
        }
        if (selected.value === '1') {
            feedback.textContent = 'Correct! +10 XP';
            feedback.style.color = 'var(--success-color)';
            // In a real app, we'd call an API to update XP here
        } else {
            feedback.textContent = 'Try again!';
            feedback.style.color = 'var(--danger-color)';
        }
    });

    // Quest Logic
    window.startQuest = (questName) => {
        alert(`Quest "${questName}" started! Good luck.`);
    };

    // Arcade Logic
    const modal = document.getElementById('game-modal');
    const closeModal = document.querySelector('.close-modal');

    window.playGame = (gameName) => {
        document.getElementById('modal-game-title').textContent = gameName;
        modal.classList.remove('hidden');
        document.getElementById('mock-score').textContent = Math.floor(Math.random() * 1000);
    };

    closeModal.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.classList.add('hidden');
        }
    };

    // Market Lab Logic
    window.predictMarket = (direction) => {
        const amount = document.getElementById('invest-amount').value;
        const resultBox = document.getElementById('market-result');

        if (amount <= 0) {
            alert('Invalid amount');
            return;
        }

        const win = Math.random() > 0.5;
        if (win) {
            resultBox.textContent = `You won! Price went ${direction}. +${amount} Coins`;
            resultBox.style.color = 'var(--success-color)';
        } else {
            resultBox.textContent = `You lost. Price went the other way. -${amount} Coins`;
            resultBox.style.color = 'var(--danger-color)';
        }
    };

    window.resetMarket = () => {
        document.getElementById('market-result').textContent = '';
        document.getElementById('invest-amount').value = 10;
    };

    // Mentor Hub (Chat)
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat-btn');
    const chatHistory = document.getElementById('chat-history');

    function addMessage(text, type) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;
        msgDiv.innerHTML = `<div class="msg-bubble">${text}</div>`;
        chatHistory.appendChild(msgDiv);
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }

    sendChatBtn.addEventListener('click', () => {
        const text = chatInput.value.trim();
        if (text) {
            addMessage(text, 'user-message');
            chatInput.value = '';

            // Call Flask API
            fetch('/ai_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: text }),
            })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.response, 'agent-message');
                })
                .catch((error) => {
                    console.error('Error:', error);
                    addMessage("Sorry, I'm having trouble connecting to the server.", 'agent-message');
                });
        }
    });

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendChatBtn.click();
    });

    // Arena Logic
    window.switchArenaTab = (tab) => {
        const tabs = document.querySelectorAll('.arena-tabs .tab-btn');
        tabs.forEach(t => t.classList.remove('active'));
        event.target.classList.add('active');
    };

});
