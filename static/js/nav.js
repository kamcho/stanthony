(function () {
    var header = document.getElementById('siteHeader');
    var toggle = document.getElementById('navToggle');
    var panel = document.getElementById('navPanel');
    var backdrop = document.getElementById('navBackdrop');

    if (!header || !toggle || !panel) return;

    function setOpen(isOpen) {
        header.classList.toggle('nav-open', isOpen);
        toggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        toggle.setAttribute('aria-label', isOpen ? 'Close menu' : 'Open menu');
        document.body.classList.toggle('nav-scroll-lock', isOpen);

        if (backdrop) {
            backdrop.hidden = !isOpen;
            backdrop.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
        }
    }

    function closeMenu() {
        setOpen(false);
    }

    toggle.addEventListener('click', function () {
        setOpen(!header.classList.contains('nav-open'));
    });

    if (backdrop) {
        backdrop.addEventListener('click', closeMenu);
    }

    panel.querySelectorAll('a').forEach(function (link) {
        link.addEventListener('click', closeMenu);
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeMenu();
    });

    window.addEventListener('resize', function () {
        if (window.innerWidth > 900) closeMenu();
    });
})();
