// Navigation & SPA Logic
function goToSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
    // Show target section
    document.getElementById(sectionId).classList.add('active');

    // Update Sidebar Active State
    document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
    const navItem = document.getElementById(`nav-${sectionId.replace('learning-', '').replace('daily-', '').replace('arcade-', '').replace('market-', '').replace('finsense-', '').replace('team-', '').replace('hall-of-', '')}`);
    if (navItem) navItem.classList.add('active');

    // Close mobile menu if open
    document.getElementById('sidebar').classList.remove('open');
}

function openDashboard() { goToSection('dashboard'); }
function openUserProfile() { goToSection('user-profile'); }
function openLearningAcademy() { goToSection('learning-academy'); }
function openDailyQuests() { goToSection('daily-quests'); }
function openArcadeGames() { goToSection('arcade-games'); }
function openMarketLab() { goToSection('market-lab'); }
function openFinSenseCoach() { goToSection('finsense-coach'); }
function openTeamArena() { goToSection('team-arena'); }
function openHallOfFame() {
    goToSection('hall-of-fame');
    loadLeaderboardData();
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

function toggleUserDropdown() {
    document.getElementById('user-dropdown').classList.toggle('hidden');
}

// Auth Logic
function switchToSignIn() {
    document.getElementById('sign-in-form').classList.add('active');
    document.getElementById('create-account-form').classList.remove('active');
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.querySelectorAll('.tab-btn')[1].classList.remove('active');
}

function switchToCreateAccount() {
    document.getElementById('sign-in-form').classList.remove('active');
    document.getElementById('create-account-form').classList.add('active');
    document.querySelectorAll('.tab-btn')[0].classList.remove('active');
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
}

function togglePasswordVisibility(icon) {
    const input = icon.previousElementSibling;
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.replace('fa-eye', 'fa-eye-slash'); // Fix logic
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

function requestEmailCodeForSignIn() {
    console.log('Requesting OTP for Sign In...');
    document.getElementById('login-otp-area').classList.remove('hidden');
}

function requestEmailCodeForRegistration() {
    console.log('Requesting OTP for Registration...');
    document.getElementById('reg-otp-area').classList.remove('hidden');
}

function submitSignInForm(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    console.log(`Signing in user: ${email}`);
    // Mock success
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('app-shell').classList.remove('hidden');
    openDashboard();
}

function submitCreateAccountForm(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    console.log(`Creating account for: ${name}`);
    // Mock success
    document.getElementById('auth-section').classList.add('hidden');
    document.getElementById('app-shell').classList.remove('hidden');
    openDashboard();
}

function handleSignOut() {
    console.log('Signing out...');
    document.getElementById('app-shell').classList.add('hidden');
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('user-dropdown').classList.add('hidden');
}

// Profile Logic
function updateUserProfile(e) {
    e.preventDefault();
    const displayName = document.getElementById('edit-display-name').value;
    console.log(`Updating profile: ${displayName}`);
    alert('Profile updated successfully!');
}

function startChangePasswordFlow() {
    console.log('Starting password change flow...');
    alert('Password change modal would open here.');
}

function confirmAccountDeletion() {
    document.getElementById('delete-account-modal').classList.remove('hidden');
}

// Feature Stubs
function selectLesson(id) {
    console.log(`Selected lesson ${id}`);
    document.getElementById('lesson-content-placeholder').classList.add('hidden');
    document.getElementById('active-lesson-content').classList.remove('hidden');
    // In real app, fetch lesson data based on ID
}

function startNewQuest(type) {
    console.log(`Starting quest: ${type}`);
    alert('Quest started! Check your progress in the dashboard.');
}

function openGameModal(gameTitle) {
    document.getElementById('modal-game-title').textContent = gameTitle;
    document.getElementById('game-modal').classList.remove('hidden');
}

function simulateMarketOutcome() {
    const instrument = document.getElementById('market-instrument').value;
    const amount = document.getElementById('market-amount').value;
    console.log(`Simulating market: ${instrument} with ${amount}`);

    const resultBox = document.getElementById('market-result-box');
    const change = (Math.random() * 20 - 10).toFixed(2); // Random -10% to +10%
    const isProfit = change > 0;

    resultBox.innerHTML = `
        <h4 class="${isProfit ? 'text-success' : 'text-danger'}">
            ${isProfit ? 'Profit' : 'Loss'}: ${change}%
        </h4>
        <p>New Value: ${(amount * (1 + change / 100)).toFixed(2)} Coins</p>
    `;
}

function resetMarketSim() {
    document.getElementById('market-result-box').innerHTML = '<p class="text-muted">Results will appear here...</p>';
}

function sendMessageToCoach(prefill = null) {
    const input = document.getElementById('coach-input');
    const text = prefill || input.value;
    if (!text) return;

    const history = document.getElementById('chat-history');

    // User Message
    const userMsg = document.createElement('div');
    userMsg.className = 'message user-msg';
    userMsg.innerHTML = `<div class="bubble">${text}</div>`;
    history.appendChild(userMsg);

    input.value = '';
    history.scrollTop = history.scrollHeight;

    // Mock Response
    setTimeout(() => {
        const coachMsg = document.createElement('div');
        coachMsg.className = 'message coach-msg';
        coachMsg.innerHTML = `<div class="bubble">That's an interesting question about "${text}". As an AI, I'm analyzing your financial data... (Placeholder)</div>`;
        history.appendChild(coachMsg);
        history.scrollTop = history.scrollHeight;
    }, 1000);
}

function createNewRoom() {
    console.log('Creating new room...');
    document.getElementById('arena-log').innerHTML = '<p class="text-success">Room created! Code: <strong>FIN-882</strong></p>';
}

function joinExistingRoom() {
    const code = document.getElementById('room-code').value;
    console.log(`Joining room: ${code}`);
    document.getElementById('arena-log').innerHTML = `<p class="text-success">Joined room ${code}!</p>`;
}

function switchArenaTab(mode) {
    console.log(`Switching arena mode to: ${mode}`);
    document.querySelectorAll('.arena-tabs-container .tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}

function loadLeaderboardData() {
    console.log('Loading leaderboard...');
    const tbody = document.getElementById('leaderboard-body');
    tbody.innerHTML = `
        <tr><td>1</td><td>AlphaWolf</td><td>15000</td><td>99</td><td>New York</td></tr>
        <tr><td>2</td><td>BetaBear</td><td>14200</td><td>95</td><td>London</td></tr>
        <tr><td>3</td><td>GammaGoat</td><td>13800</td><td>92</td><td>Mumbai</td></tr>
    `;
}

function toggleColorTheme() {
    document.body.classList.toggle('light-mode');
    console.log('Toggled theme');
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', dateOptions);
});
