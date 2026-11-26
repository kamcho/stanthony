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
