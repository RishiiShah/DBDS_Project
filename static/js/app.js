/* ── BuyMe Global JS ─── */
document.addEventListener('DOMContentLoaded', () => {
  // Mobile nav toggle
  const toggle = document.getElementById('nav-toggle');
  const menu = document.getElementById('nav-menu');
  if (toggle && menu) {
    toggle.addEventListener('click', () => menu.classList.toggle('active'));
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
