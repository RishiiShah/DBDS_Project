/**
 * search.js — Dynamic filters, live search, and sort toggle
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-filter-form');
    if (!form) return;

    // ── Live search with debounce ───────────────────────────────────
    const keywordInput = form.querySelector('input[name="q"]');
    let debounceTimer = null;

    if (keywordInput) {
        keywordInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                form.submit();
            }, 600);
        });
    }

    // ── Auto-submit on filter change ────────────────────────────────
    const autoSubmitFields = form.querySelectorAll('select');
    autoSubmitFields.forEach(field => {
        field.addEventListener('change', () => form.submit());
    });
});
