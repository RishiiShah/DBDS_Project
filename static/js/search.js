/**
 * search.js — Filter modal toggle; form submits only on explicit button click.
 */

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('search-filter-form');
    if (!form) return;

    // Prevent any accidental implicit submission from Enter key on number inputs
    // (Enter on the text search input is intentional and fine — browsers submit normally)
    form.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('keydown', e => {
            if (e.key === 'Enter') e.preventDefault();
        });
    });
});
