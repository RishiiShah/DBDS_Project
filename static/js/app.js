/* ── BuyMe Global JS ─── */
document.addEventListener('DOMContentLoaded', () => {
  // Mobile nav toggle
  const toggle = document.getElementById('nav-toggle');
  const menu = document.getElementById('nav-menu');
  if (toggle && menu) {
    toggle.addEventListener('click', () => menu.classList.toggle('active'));
  }

  // User dropdown
  const dropdown = document.getElementById('nav-dropdown');
  const dropdownTrigger = document.getElementById('dropdown-trigger');
  if (dropdown && dropdownTrigger) {
    dropdownTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      dropdown.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
      if (dropdown && !dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
      }
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') dropdown.classList.remove('open');
    });
  }

  // Auto-dismiss flash messages after 5s
  document.querySelectorAll('.flash').forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0';
      el.style.transform = 'translateX(30px)';
      setTimeout(() => el.remove(), 300);
    }, 5000);
  });
});
