/* === theme.js === */
(function () {
    const STORAGE_KEY = 'stanthony-theme';
    const root = document.documentElement;
    const toggle = document.getElementById('themeToggle');

    function getPreferredTheme() {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored === 'light' || stored === 'dark') {
            return stored;
        }
        return 'light';
    }

    function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        localStorage.setItem(STORAGE_KEY, theme);
    }

    applyTheme(getPreferredTheme());

    if (toggle) {
        toggle.addEventListener('click', function () {
            const current = root.getAttribute('data-theme');
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });
    }
})();

/* === nav.js === */
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

/* === hero-rotator.js === */
(function () {
    var rotator = document.getElementById('heroRotator');
    if (!rotator) return;

    var slides = Array.prototype.slice.call(rotator.querySelectorAll('.hero-slide'));
    if (slides.length < 2) return;

    var interval = parseInt(rotator.getAttribute('data-interval'), 10) || 5000;
    var index = slides.findIndex(function (slide) {
        return slide.classList.contains('is-active');
    });
    if (index < 0) index = 0;

    var timer = null;
    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function show(next) {
        slides.forEach(function (slide, i) {
            var active = i === next;
            slide.classList.toggle('is-active', active);
            slide.setAttribute('aria-hidden', active ? 'false' : 'true');
        });
        index = next;
    }

    function advance() {
        show((index + 1) % slides.length);
    }

    function start() {
        if (reduceMotion || timer) return;
        timer = window.setInterval(advance, interval);
    }

    function stop() {
        if (!timer) return;
        window.clearInterval(timer);
        timer = null;
    }

    rotator.addEventListener('mouseenter', stop);
    rotator.addEventListener('mouseleave', start);
    rotator.addEventListener('focusin', stop);
    rotator.addEventListener('focusout', function (event) {
        if (!rotator.contains(event.relatedTarget)) start();
    });

    document.addEventListener('visibilitychange', function () {
        if (document.hidden) stop();
        else start();
    });

    start();
})();

