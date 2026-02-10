/**
 * practice.js — Custom practice builder + full-screen practice player.
 * Features: drag-and-drop queue, countdown timer, voice announcements,
 * play/pause/skip controls, circular timer animation.
 */
const PracticeView = (() => {
    // ─── State ─────────────────────────────────
    let queue = [];          // [{pose_id, english_name, sanskrit_name, side, hold_seconds, category, tags}]
    let searchDebounce = null;

    // Player state
    let isPlaying = false;
    let currentIndex = 0;
    let secondsLeft = 0;
    let totalSeconds = 0;
    let timerInterval = null;
    let voiceEnabled = true;

    // ─── Init ──────────────────────────────────
    function init() {
        bindEvents();
    }

    function bindEvents() {
        document.getElementById('practice-pose-search').addEventListener('input', (e) => {
            clearTimeout(searchDebounce);
            searchDebounce = setTimeout(() => searchPoses(e.target.value), 250);
        });
        document.getElementById('start-practice-btn').addEventListener('click', startPractice);
        document.getElementById('exit-practice').addEventListener('click', exitPractice);
        document.getElementById('btn-play-pause').addEventListener('click', togglePlayPause);
        document.getElementById('btn-next').addEventListener('click', nextPose);
        document.getElementById('btn-prev').addEventListener('click', prevPose);
        document.getElementById('voice-toggle').addEventListener('change', (e) => {
            voiceEnabled = e.target.checked;
        });
        document.getElementById('load-practice-btn').addEventListener('click', showLoadModal);
        document.getElementById('load-modal-close').addEventListener('click', () => {
            document.getElementById('load-practice-modal').style.display = 'none';
        });
    }

    // ─── Practice search ───────────────────────
    async function searchPoses(q) {
        if (!q || q.length < 2) {
            document.getElementById('practice-search-results').innerHTML = '';
            return;
        }
        const data = await API.getPoses({ q, per_page: 20 });
        const results = document.getElementById('practice-search-results');
        results.innerHTML = data.poses.map(p => `
            <div class="practice-search-item">
                <div>
                    <strong>${p.english_name}</strong>
                    <span style="color:var(--text-dim);font-size:0.8rem;"> · ${p.category}</span>
                </div>
                <button class="add-btn" onclick='PracticeView.addPoseToQueue(${JSON.stringify({
            id: p.id,
            english_name: p.english_name,
            sanskrit_name: p.sanskrit_name,
            category: p.category,
            default_hold_seconds: p.default_hold_seconds,
            is_bilateral: p.is_bilateral,
            tags: p.tags || [],
        }).replace(/'/g, "\\'")})'}>+ Add</button>
            </div>
        `).join('');
    }

    // ─── Queue Management ──────────────────────
    function addPoseToQueue(pose) {
        // If bilateral, add both sides
        if (pose.is_bilateral) {
            queue.push({
                pose_id: pose.id,
                english_name: pose.english_name,
                sanskrit_name: pose.sanskrit_name,
                category: pose.category,
                tags: pose.tags || [],
                side: 'left',
                hold_seconds: pose.default_hold_seconds || 30,
            });
            queue.push({
                pose_id: pose.id,
                english_name: pose.english_name,
                sanskrit_name: pose.sanskrit_name,
                category: pose.category,
                tags: pose.tags || [],
                side: 'right',
                hold_seconds: pose.default_hold_seconds || 30,
            });
        } else {
            queue.push({
                pose_id: pose.id,
                english_name: pose.english_name,
                sanskrit_name: pose.sanskrit_name,
                category: pose.category,
                tags: pose.tags || [],
                side: 'both',
                hold_seconds: pose.default_hold_seconds || 30,
            });
        }
        renderQueue();
        // Close modal if open
        document.getElementById('pose-modal').style.display = 'none';
    }

    function removeFromQueue(index) {
        queue.splice(index, 1);
        renderQueue();
    }

    function updateHoldTime(index, value) {
        const seconds = parseInt(value);
        if (!isNaN(seconds) && seconds > 0) {
            queue[index].hold_seconds = seconds;
            updateSummary();
        }
    }

    function renderQueue() {
        const list = document.getElementById('practice-queue-list');
        const startBtn = document.getElementById('start-practice-btn');
        const countEl = document.getElementById('queue-count');

        countEl.textContent = `(${queue.length} poses)`;
        startBtn.disabled = queue.length === 0;

        if (queue.length === 0) {
            list.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:20px;font-size:0.85rem;">Search and add poses to build your practice.</p>';
            document.getElementById('practice-summary').style.display = 'none';
            return;
        }

        list.innerHTML = queue.map((p, i) => {
            const sideLabel = p.side !== 'both' ? ` (${p.side})` : '';
            return `
                <div class="queue-item" draggable="true" data-index="${i}"
                     ondragstart="PracticeView.dragStart(event, ${i})"
                     ondragover="PracticeView.dragOver(event)"
                     ondrop="PracticeView.drop(event, ${i})">
                    <span class="grip">⠿</span>
                    <div class="q-info">
                        <span class="q-name">${p.english_name}${sideLabel}</span>
                        <span class="q-meta">${p.sanskrit_name || ''}</span>
                    </div>
                    <input type="number" class="q-time" value="${p.hold_seconds}" min="5" max="600"
                           onchange="PracticeView.updateHoldTime(${i}, this.value)">
                    <button class="q-remove" onclick="PracticeView.removeFromQueue(${i})">✕</button>
                </div>
            `;
        }).join('');

        updateSummary();
    }

    function updateSummary() {
        const total = queue.reduce((s, p) => s + p.hold_seconds, 0);
        const min = Math.floor(total / 60);
        const sec = total % 60;
        document.getElementById('total-duration').textContent = `Total: ${min}m ${sec}s`;
        document.getElementById('practice-summary').style.display = 'block';
    }

    // ─── Drag & Drop ───────────────────────────
    let dragIdx = null;
    function dragStart(e, idx) {
        dragIdx = idx;
        e.target.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
    }
    function dragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    }
    function drop(e, dropIdx) {
        e.preventDefault();
        if (dragIdx === null || dragIdx === dropIdx) return;
        const item = queue.splice(dragIdx, 1)[0];
        queue.splice(dropIdx, 0, item);
        dragIdx = null;
        renderQueue();
    }

    // ─── Load from sequence ────────────────────
    function loadFromSequence(poses) {
        queue = poses.map(p => ({
            pose_id: p.pose_id,
            english_name: p.english_name,
            sanskrit_name: p.sanskrit_name,
            category: p.category || '',
            tags: p.tags || [],
            side: p.side || 'both',
            hold_seconds: p.hold_seconds || 30,
        }));
        renderQueue();
    }

    async function showLoadModal() {
        const modal = document.getElementById('load-practice-modal');
        const list = document.getElementById('load-practice-list');
        list.innerHTML = '<p style="color:var(--text-dim);">Loading...</p>';
        modal.style.display = 'flex';

        const [practices, sequences] = await Promise.all([
            API.getPractices(),
            API.getSequences(),
        ]);

        let html = '';
        if (practices.length > 0) {
            html += '<h4 style="color:var(--text-dim);margin:8px 0;">My Practices</h4>';
            html += practices.map(p => `
                <div class="load-item" onclick="PracticeView.loadPractice(${p.id})">
                    <div>
                        <strong>${p.name}</strong>
                        <div style="font-size:0.8rem;color:var(--text-dim);">${p.pose_count || 0} poses</div>
                    </div>
                    <button class="btn btn-sm btn-danger" onclick="event.stopPropagation();PracticeView.deletePractice(${p.id})">Delete</button>
                </div>
            `).join('');
        }
        if (sequences.length > 0) {
            html += '<h4 style="color:var(--text-dim);margin:8px 0;">Saved Sequences</h4>';
            html += sequences.map(s => `
                <div class="load-item" onclick="PracticeView.loadSequenceById(${s.id})">
                    <strong>${s.name}</strong>
                    <span style="font-size:0.8rem;color:var(--text-dim);">${s.pose_count} poses</span>
                </div>
            `).join('');
        }
        if (!html) html = '<p style="color:var(--text-dim);">No saved practices or sequences.</p>';
        list.innerHTML = html;
    }

    async function loadPractice(id) {
        const data = await API.getPractice(id);
        loadFromSequence(data.poses);
        document.getElementById('load-practice-modal').style.display = 'none';
    }

    async function loadSequenceById(id) {
        const data = await API.getSequence(id);
        loadFromSequence(data.poses);
        document.getElementById('load-practice-modal').style.display = 'none';
    }

    async function deletePractice(id) {
        if (!confirm('Delete this practice?')) return;
        await API.deletePractice(id);
        showLoadModal();
    }

    // ─── Practice Player ───────────────────────
    function startPractice() {
        if (queue.length === 0) return;
        currentIndex = 0;
        isPlaying = true;
        document.getElementById('practice-builder').style.display = 'none';
        document.getElementById('practice-player').style.display = 'flex';
        loadCurrentPose();
        play();
    }

    function exitPractice() {
        pause();
        isPlaying = false;
        document.getElementById('practice-player').style.display = 'none';
        document.getElementById('practice-builder').style.display = 'block';
    }

    function loadCurrentPose() {
        const pose = queue[currentIndex];
        if (!pose) { finishPractice(); return; }

        secondsLeft = pose.hold_seconds;
        totalSeconds = pose.hold_seconds;

        // Update display
        document.getElementById('player-pose-name').textContent = pose.english_name;
        document.getElementById('player-pose-sanskrit').textContent = pose.sanskrit_name || '';
        document.getElementById('player-pose-side').textContent =
            pose.side !== 'both' ? `${pose.side.toUpperCase()} SIDE` : '';
        document.getElementById('player-pose-svg').innerHTML = SVGPoses.getSVG(pose, 120);
        document.getElementById('timer-text').textContent = formatTimer(secondsLeft);

        // Phase
        const phase = getPhase(currentIndex);
        const phaseEl = document.getElementById('player-phase');
        phaseEl.textContent = phase;
        phaseEl.className = 'player-phase ' + phase;

        // Progress
        updateProgress();

        // Next up
        const next = queue[currentIndex + 1];
        document.getElementById('player-next-up').textContent = next
            ? `Next: ${next.english_name}${next.side !== 'both' ? ` (${next.side})` : ''}`
            : 'Last pose';

        // Timer ring
        updateTimerRing();

        // Voice
        if (voiceEnabled) {
            let text = pose.english_name;
            if (pose.side !== 'both') text += `, ${pose.side} side`;
            speak(text);
        }
    }

    function getPhase(index) {
        const ratio = index / queue.length;
        if (ratio < 0.25) return 'warmup';
        if (ratio < 0.75) return 'peak';
        return 'cooldown';
    }

    function play() {
        isPlaying = true;
        showPlayIcon(false);
        timerInterval = setInterval(tick, 1000);
    }

    function pause() {
        isPlaying = false;
        showPlayIcon(true);
        clearInterval(timerInterval);
    }

    function togglePlayPause() {
        if (isPlaying) pause();
        else play();
    }

    function tick() {
        secondsLeft--;
        if (secondsLeft <= 0) {
            clearInterval(timerInterval);
            currentIndex++;
            if (currentIndex >= queue.length) {
                finishPractice();
                return;
            }
            loadCurrentPose();
            if (isPlaying) play();
            return;
        }

        document.getElementById('timer-text').textContent = formatTimer(secondsLeft);
        updateTimerRing();
        updateProgress();

        // Countdown warnings
        if (voiceEnabled && secondsLeft === 5) speak('Five seconds');
        if (voiceEnabled && secondsLeft === 3) speak('Three');
    }

    function updateTimerRing() {
        const circle = document.getElementById('timer-circle');
        const circumference = 2 * Math.PI * 90; // r=90
        const progress = secondsLeft / totalSeconds;
        circle.style.strokeDashoffset = circumference * (1 - progress);
    }

    function updateProgress() {
        const ratio = currentIndex / queue.length;
        document.getElementById('player-progress-fill').style.width = `${ratio * 100}%`;
        document.getElementById('player-progress-text').textContent =
            `${currentIndex + 1} / ${queue.length}`;
    }

    function nextPose() {
        clearInterval(timerInterval);
        currentIndex++;
        if (currentIndex >= queue.length) { finishPractice(); return; }
        loadCurrentPose();
        if (isPlaying) play();
    }

    function prevPose() {
        clearInterval(timerInterval);
        currentIndex = Math.max(0, currentIndex - 1);
        loadCurrentPose();
        if (isPlaying) play();
    }

    function finishPractice() {
        pause();
        if (voiceEnabled) speak('Practice complete. Namaste.');
        document.getElementById('player-pose-name').textContent = '🙏 Practice Complete';
        document.getElementById('player-pose-sanskrit').textContent = 'Namaste';
        document.getElementById('player-pose-side').textContent = '';
        document.getElementById('timer-text').textContent = '✓';
        document.getElementById('player-next-up').textContent = '';
        document.getElementById('player-progress-fill').style.width = '100%';
        document.getElementById('player-progress-text').textContent = 'Done';
    }

    function showPlayIcon(show) {
        document.getElementById('icon-play').style.display = show ? 'block' : 'none';
        document.getElementById('icon-pause').style.display = show ? 'none' : 'block';
    }

    // ─── Voice ─────────────────────────────────
    function speak(text) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 0.9;
        utter.pitch = 1.0;
        utter.volume = 0.8;
        window.speechSynthesis.speak(utter);
    }

    // ─── Helpers ───────────────────────────────
    function formatTimer(sec) {
        const m = Math.floor(sec / 60);
        const s = sec % 60;
        return `${m}:${s.toString().padStart(2, '0')}`;
    }

    // ─── Public API ────────────────────────────
    return {
        init,
        addPoseToQueue,
        removeFromQueue,
        updateHoldTime,
        loadFromSequence,
        loadPractice,
        loadSequenceById,
        deletePractice,
        dragStart,
        dragOver,
        drop,
    };
})();
