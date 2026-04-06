/* ==========================================================================
   CombatPrep — Main JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {

    // ---- Sidebar Toggle (mobile) ----
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
        });
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') &&
                !sidebar.contains(e.target) &&
                e.target !== toggle) {
                sidebar.classList.remove('open');
            }
        });
    }

    // ---- Auto-dismiss alerts after 5s ----
    document.querySelectorAll('.alert').forEach((el, i) => {
        setTimeout(() => {
            el.style.transition = 'opacity .4s ease, transform .4s ease';
            el.style.opacity = '0';
            el.style.transform = 'translateY(-8px)';
            setTimeout(() => el.remove(), 400);
        }, 5000 + i * 500);
    });

    // ---- Live Score Preview ----
    const scoreForm = document.getElementById('score-form');
    if (scoreForm) {
        const physical = scoreForm.querySelector('#id_physical_score');
        const mental   = scoreForm.querySelector('#id_mental_score');
        const equip    = scoreForm.querySelector('#id_equipment_score');
        const preview  = document.getElementById('preview-overall');
        const level    = document.getElementById('preview-level');

        function updatePreview() {
            const p = parseFloat(physical?.value) || 0;
            const m = parseFloat(mental?.value)   || 0;
            const e = parseFloat(equip?.value)    || 0;

            if (!physical?.value && !mental?.value && !equip?.value) {
                preview.textContent = '—';
                level.textContent = '';
                level.style.color = '';
                return;
            }

            const overall = (p * 0.40 + m * 0.35 + e * 0.25).toFixed(2);
            preview.textContent = overall;

            let lbl, clr;
            if (overall >= 85)      { lbl = 'Combat Ready';      clr = '#6ee7b7'; }
            else if (overall >= 70) { lbl = 'Mostly Ready';      clr = '#93c5fd'; }
            else if (overall >= 50) { lbl = 'Needs Improvement'; clr = '#fcd34d'; }
            else                    { lbl = 'Not Ready';         clr = '#fca5a5'; }
            level.textContent = lbl;
            level.style.color = clr;
        }

        [physical, mental, equip].forEach(el => {
            if (el) el.addEventListener('input', updatePreview);
        });
        updatePreview();
    }

    // ---- Animate stat values on scroll into view ----
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeUp .5s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.stat-card, .card').forEach(el => observer.observe(el));
});
