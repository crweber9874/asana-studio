/**
 * sequences.js — Sequence generator & saved sequences.
 */
const SequencesView = (() => {
    let currentGenerated = null;

    async function init() {
        await loadStyles();
        loadSaved();
        bindEvents();
    }

    function bindEvents() {
        document.getElementById('generate-sequence').addEventListener('click', generate);
    }

    async function loadStyles() {
        const styles = await API.getStyles();
        const select = document.getElementById('seq-style');
        select.innerHTML = styles.map(s =>
            `<option value="${s.id}">${s.name}</option>`
        ).join('');
    }

    async function generate() {
        const btn = document.getElementById('generate-sequence');
        btn.textContent = '⏳ Generating...';
        btn.disabled = true;

        try {
            const data = await API.generateSequence({
                style: document.getElementById('seq-style').value,
                duration_minutes: parseInt(document.getElementById('seq-duration').value),
                difficulty: parseInt(document.getElementById('seq-difficulty').value),
            });
            currentGenerated = data;
            renderGenerated(data);
        } catch (err) {
            alert('Error generating sequence: ' + err.message);
        }

        btn.textContent = '✨ Generate Sequence';
        btn.disabled = false;
    }

    function renderGenerated(data) {
        const container = document.getElementById('generated-sequence');
        container.style.display = 'block';

        const totalMin = data.duration_minutes;
        container.innerHTML = `
            <div class="seq-result-header">
                <div>
                    <h3>${data.style_name}</h3>
                    <p style="color:var(--text-dim);font-size:0.85rem;">
                        ${data.total_poses} poses · ~${totalMin} min · Max difficulty: ${'★'.repeat(data.difficulty)}
                    </p>
                </div>
                <div class="seq-result-actions">
                    <button class="btn btn-ghost btn-sm" onclick="SequencesView.saveGenerated()">💾 Save</button>
                    <button class="btn btn-primary btn-sm" onclick="SequencesView.practiceGenerated()">▶ Practice</button>
                </div>
            </div>
            <div class="seq-pose-list">
                ${data.poses.map(p => {
            const sideLabel = p.side !== 'both' ? ` <span style="color:var(--warning);">(${p.side})</span>` : '';
            return `
                        <div class="seq-pose-item phase-${p.phase}">
                            <span class="seq-pose-num">${p.position}</span>
                            <div class="seq-pose-info">
                                <span class="name">${p.english_name}${sideLabel}</span>
                                <span class="meta">${p.sanskrit_name || ''} · ${p.phase}</span>
                            </div>
                            <span class="seq-pose-time">${formatTime(p.hold_seconds)}</span>
                        </div>
                    `;
        }).join('')}
            </div>
        `;
    }

    async function saveGenerated() {
        if (!currentGenerated) return;
        const name = prompt('Name this sequence:', currentGenerated.style_name);
        if (!name) return;

        try {
            await API.saveSequence({
                name,
                description: `${currentGenerated.style_name} · ${currentGenerated.total_poses} poses`,
                style: currentGenerated.style,
                difficulty: currentGenerated.difficulty,
                poses: currentGenerated.poses.map(p => ({
                    pose_id: p.pose_id,
                    position: p.position,
                    side: p.side,
                    hold_seconds: p.hold_seconds,
                })),
            });
            alert('Sequence saved!');
            loadSaved();
        } catch (err) {
            alert('Error saving: ' + err.message);
        }
    }

    function practiceGenerated() {
        if (!currentGenerated) return;
        PracticeView.loadFromSequence(currentGenerated.poses);
        // Switch to practice tab
        document.querySelector('[data-tab="practice"]').click();
    }

    async function loadSaved() {
        const seqs = await API.getSequences();
        const list = document.getElementById('saved-list');
        if (seqs.length === 0) {
            list.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No saved sequences yet.</p>';
            return;
        }
        list.innerHTML = seqs.map(s => `
            <div class="saved-seq-card" onclick="SequencesView.viewSaved(${s.id})">
                <div>
                    <strong>${s.name}</strong>
                    <div style="font-size:0.8rem;color:var(--text-dim);">${s.style || ''} · ${s.pose_count} poses · ${'★'.repeat(s.difficulty)}</div>
                </div>
                <span style="font-size:0.78rem;color:var(--text-muted);">${s.created_at || ''}</span>
            </div>
        `).join('');
    }

    async function viewSaved(id) {
        const seq = await API.getSequence(id);
        currentGenerated = {
            ...seq,
            style_name: seq.name,
            total_poses: seq.poses.length,
            duration_minutes: Math.round(seq.poses.reduce((s, p) => s + p.hold_seconds, 0) / 60 * 10) / 10,
        };
        // Add phase info for rendering
        currentGenerated.poses = seq.poses.map((p, i) => ({
            ...p,
            phase: i < seq.poses.length * 0.25 ? 'warmup' : i < seq.poses.length * 0.75 ? 'peak' : 'cooldown',
        }));
        renderGenerated(currentGenerated);
    }

    function formatTime(seconds) {
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return m > 0 ? `${m}:${s.toString().padStart(2, '0')}` : `${s}s`;
    }

    return { init, saveGenerated, practiceGenerated, viewSaved };
})();
