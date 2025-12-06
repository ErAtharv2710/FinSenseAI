const dashboard = {
    async init() {
        if (!auth.user) return;

        const uid = auth.user.uid;
        const userDoc = await db.collection('users').doc(uid).get();
        const userData = userDoc.data();

        this.renderHero(userData);
        this.renderSnapshot(userData);
    },

    renderHero(data) {
        const content = document.getElementById('dashboard-content');
        content.innerHTML = `
            <div class="glass-card mb-4">
                <div class="flex-center" style="justify-content: space-between;">
                    <div>
                        <h2>Welcome back, ${data.username}!</h2>
                        <p class="text-muted">Level ${data.level} • ${data.xp} XP</p>
                    </div>
                    <div class="level-ring">
                        <!-- Ring Chart Placeholder -->
                        <div style="width:60px; height:60px; border: 4px solid var(--primary); border-radius:50%; display:flex; align-items:center; justify-content:center;">
                            ${data.level}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="grid-layout" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                <div class="glass-card">
                    <h3><i class="fas fa-chart-pie text-accent"></i> Spending Snapshot</h3>
                    <div id="snapshot-chart">Loading...</div>
                </div>
                
                <div class="glass-card">
                    <h3><i class="fas fa-lightbulb text-primary"></i> Coach's Tip</h3>
                    <p id="daily-tip">"The sooner you start saving, the better due to compound interest!"</p>
                </div>
            </div>
        `;
    },

    renderSnapshot(data) {
        // Mock Snapshot Visualization
        const chart = document.getElementById('snapshot-chart');
        chart.innerHTML = `
            <div style="margin-top: 1rem;">
                <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                    <span>Needs</span>
                    <span>50%</span>
                </div>
                <div style="height:8px; background:rgba(255,255,255,0.1); border-radius:4px; overflow:hidden;">
                    <div style="width:50%; height:100%; background:#3B82F6;"></div>
                </div>
                
                <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; margin-top:1rem;">
                    <span>Wants</span>
                    <span>30%</span>
                </div>
                <div style="height:8px; background:rgba(255,255,255,0.1); border-radius:4px; overflow:hidden;">
                    <div style="width:30%; height:100%; background:#F59E0B;"></div>
                </div>

                <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem; margin-top:1rem;">
                    <span>Savings</span>
                    <span>20%</span>
                </div>
                <div style="height:8px; background:rgba(255,255,255,0.1); border-radius:4px; overflow:hidden;">
                    <div style="width:20%; height:100%; background:#10B981;"></div>
                </div>
            </div>
        `;
    }
};

// Hook into router to load dashboard when screen is shown
const originalGoToScreen = router.goToScreen;
router.goToScreen = function (screenId) {
    originalGoToScreen.call(router, screenId);
    if (screenId === 'dashboardScreen') {
        dashboard.init();
    }
};
