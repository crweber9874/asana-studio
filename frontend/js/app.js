/**
 * app.js — Main application: tab routing and initialization.
 */
document.addEventListener('DOMContentLoaded', async () => {
    // ─── Tab Navigation ────────────────────────
    const navBtns = document.querySelectorAll('.nav-btn');
    const tabs = document.querySelectorAll('.tab-content');

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            navBtns.forEach(b => b.classList.remove('active'));
            tabs.forEach(t => t.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(`tab-${tabId}`).classList.add('active');
        });
    });

    // ─── Initialize Modules ────────────────────
    try {
        await PosesView.init();
        await SequencesView.init();
        PracticeView.init();
    } catch (err) {
        console.error('Initialization error:', err);
    }
});
