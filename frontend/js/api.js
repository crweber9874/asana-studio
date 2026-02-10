/**
 * api.js — Fetch wrapper for Asana Studio API.
 */
const API = (() => {
    const BASE = '/api';

    async function request(path, options = {}) {
        const url = `${BASE}${path}`;
        const res = await fetch(url, {
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options,
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || 'API error');
        }
        return res.json();
    }

    return {
        // Poses
        getPoses: (params = {}) => {
            const qs = new URLSearchParams(params).toString();
            return request(`/poses?${qs}`);
        },
        getPose: (id) => request(`/poses/${id}`),
        getCategories: () => request('/poses/categories'),
        getTags: () => request('/poses/tags'),

        // Sequences
        getStyles: () => request('/sequences/styles'),
        generateSequence: (data) => request('/sequences/generate', {
            method: 'POST', body: JSON.stringify(data),
        }),
        saveSequence: (data) => request('/sequences', {
            method: 'POST', body: JSON.stringify(data),
        }),
        getSequences: () => request('/sequences'),
        getSequence: (id) => request(`/sequences/${id}`),

        // Practices
        createPractice: (data) => request('/practices', {
            method: 'POST', body: JSON.stringify(data),
        }),
        getPractices: () => request('/practices'),
        getPractice: (id) => request(`/practices/${id}`),
        updatePractice: (id, data) => request(`/practices/${id}`, {
            method: 'PUT', body: JSON.stringify(data),
        }),
        deletePractice: (id) => request(`/practices/${id}`, { method: 'DELETE' }),
    };
})();
