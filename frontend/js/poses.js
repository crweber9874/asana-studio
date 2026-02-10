/**
 * poses.js — Pose explorer: search, filter, paginate, detail modal.
 */
const PosesView = (() => {
    let currentPage = 1;
    let debounceTimer = null;

    async function init() {
        await loadFilters();
        await loadPoses();
        bindEvents();
    }

    function bindEvents() {
        document.getElementById('pose-search').addEventListener('input', (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => { currentPage = 1; loadPoses(); }, 300);
        });
        document.getElementById('filter-category').addEventListener('change', () => { currentPage = 1; loadPoses(); });
        document.getElementById('filter-difficulty').addEventListener('change', () => { currentPage = 1; loadPoses(); });
        document.getElementById('filter-tag').addEventListener('change', () => { currentPage = 1; loadPoses(); });
        document.getElementById('clear-filters').addEventListener('click', clearFilters);
        document.getElementById('modal-close').addEventListener('click', closeModal);
        document.getElementById('pose-modal').addEventListener('click', (e) => {
            if (e.target.id === 'pose-modal') closeModal();
        });
    }

    async function loadFilters() {
        const [categories, tags] = await Promise.all([
            API.getCategories(),
            API.getTags(),
        ]);
        const catSelect = document.getElementById('filter-category');
        categories.forEach(c => {
            catSelect.innerHTML += `<option value="${c.category}">${c.category} (${c.count})</option>`;
        });
        const tagSelect = document.getElementById('filter-tag');
        tags.forEach(t => {
            tagSelect.innerHTML += `<option value="${t.tag}">${t.tag} (${t.count})</option>`;
        });
    }

    function getFilters() {
        const params = { page: currentPage, per_page: 48 };
        const q = document.getElementById('pose-search').value.trim();
        const cat = document.getElementById('filter-category').value;
        const diff = document.getElementById('filter-difficulty').value;
        const tag = document.getElementById('filter-tag').value;
        if (q) params.q = q;
        if (cat) params.category = cat;
        if (diff) params.difficulty = diff;
        if (tag) params.tag = tag;
        return params;
    }

    async function loadPoses() {
        const data = await API.getPoses(getFilters());
        renderPoses(data);
        renderPagination(data);
    }

    function renderPoses(data) {
        const grid = document.getElementById('pose-grid');
        document.getElementById('pose-count').textContent = `${data.total} poses found`;

        if (data.poses.length === 0) {
            grid.innerHTML = '<p style="color:var(--text-dim);grid-column:1/-1;text-align:center;padding:40px;">No poses match your filters.</p>';
            return;
        }

        grid.innerHTML = data.poses.map(p => `
            <div class="pose-card" data-id="${p.id}" onclick="PosesView.showDetail(${p.id})">
                <div class="pose-card-svg">${SVGPoses.getSVG(p, 60)}</div>
                <div class="pose-card-header">
                    <div>
                        <h3>${p.english_name}</h3>
                        ${p.sanskrit_name ? `<span class="sanskrit">${p.sanskrit_name}</span>` : ''}
                    </div>
                    <span class="difficulty-badge diff-${p.difficulty}">${'★'.repeat(p.difficulty)}</span>
                </div>
                <p class="desc">${p.description || ''}</p>
                <div class="tags">
                    <span class="tag-chip">${p.category}</span>
                    ${(p.tags || []).slice(0, 3).map(t => `<span class="tag-chip">${t}</span>`).join('')}
                </div>
            </div>
        `).join('');
    }

    function renderPagination(data) {
        const container = document.getElementById('pagination');
        if (data.pages <= 1) { container.innerHTML = ''; return; }
        let html = '';
        for (let i = 1; i <= data.pages; i++) {
            html += `<button class="${i === data.page ? 'active' : ''}" onclick="PosesView.goToPage(${i})">${i}</button>`;
        }
        container.innerHTML = html;
    }

    function goToPage(page) {
        currentPage = page;
        loadPoses();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    async function showDetail(id) {
        const pose = await API.getPose(id);
        const modal = document.getElementById('pose-modal');
        const content = document.getElementById('modal-content');

        content.innerHTML = `
            <div class="modal-pose-svg">${SVGPoses.getSVG(pose, 150)}</div>
            <div class="modal-pose-header">
                <h2>${pose.english_name}</h2>
                ${pose.sanskrit_name ? `<p class="sanskrit">${pose.sanskrit_name}</p>` : ''}
            </div>
            <div class="modal-pose-meta">
                <span class="meta-item">${pose.category}</span>
                <span class="meta-item difficulty-badge diff-${pose.difficulty}">${'★'.repeat(pose.difficulty)} Level ${pose.difficulty}</span>
                <span class="meta-item">${pose.default_hold_seconds}s hold</span>
                ${pose.is_bilateral ? '<span class="meta-item">↔ Bilateral</span>' : ''}
            </div>
            <div class="modal-pose-body">
                <p>${pose.description || 'No description available.'}</p>
            </div>
            <div class="tags" style="margin-top:16px;">
                ${(pose.tags || []).map(t => `<span class="tag-chip">${t}</span>`).join('')}
            </div>
            ${pose.variations && pose.variations.length > 0 ? `
                <div class="modal-variations">
                    <h4>Variations</h4>
                    <ul>${pose.variations.map(v => `<li>${v.english_name} ${v.sanskrit_name ? `<span class="sanskrit">— ${v.sanskrit_name}</span>` : ''}</li>`).join('')}</ul>
                </div>
            ` : ''}
            ${pose.parent ? `<p style="margin-top:12px;color:var(--text-dim);font-size:0.85rem;">Variation of: <strong>${pose.parent.english_name}</strong></p>` : ''}
            <button class="btn btn-primary btn-sm modal-add-btn" onclick="PracticeView.addPoseToQueue(${JSON.stringify(pose).replace(/"/g, '&quot;')})">+ Add to Practice</button>
        `;

        modal.style.display = 'flex';
    }

    function closeModal() {
        document.getElementById('pose-modal').style.display = 'none';
    }

    function clearFilters() {
        document.getElementById('pose-search').value = '';
        document.getElementById('filter-category').value = '';
        document.getElementById('filter-difficulty').value = '';
        document.getElementById('filter-tag').value = '';
        currentPage = 1;
        loadPoses();
    }

    return { init, goToPage, showDetail, closeModal, loadPoses };
})();
