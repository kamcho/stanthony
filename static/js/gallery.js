(function () {
    var grid = document.getElementById('galleryGrid');
    if (!grid) return;

    var lightbox = document.getElementById('galleryLightbox');
    var lightboxImage = document.getElementById('lightboxImage');
    var lightboxTitle = document.getElementById('lightboxTitle');
    var lightboxCaption = document.getElementById('lightboxCaption');
    var lightboxCategory = document.getElementById('lightboxCategory');
    var prevBtn = document.getElementById('lightboxPrev');
    var nextBtn = document.getElementById('lightboxNext');
    var filters = document.querySelectorAll('.gallery-filter');
    var items = Array.from(grid.querySelectorAll('.gallery-item'));
    var visibleItems = items.slice();
    var currentIndex = 0;

    function getVisibleItems() {
        return items.filter(function (item) {
            return item.style.display !== 'none';
        });
    }

    function openLightbox(index) {
        visibleItems = getVisibleItems();
        if (!visibleItems.length) return;

        currentIndex = index;
        var item = visibleItems[currentIndex];
        lightboxImage.src = item.dataset.image;
        lightboxImage.alt = item.dataset.title;
        lightboxTitle.textContent = item.dataset.title;
        lightboxCaption.textContent = item.dataset.caption || '';
        lightboxCategory.textContent = item.querySelector('.gallery-item-category')
            ? item.querySelector('.gallery-item-category').textContent
            : '';
        lightbox.hidden = false;
        lightbox.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.hidden = true;
        lightbox.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        lightboxImage.src = '';
    }

    function showNext() {
        visibleItems = getVisibleItems();
        currentIndex = (currentIndex + 1) % visibleItems.length;
        openLightbox(currentIndex);
    }

    function showPrev() {
        visibleItems = getVisibleItems();
        currentIndex = (currentIndex - 1 + visibleItems.length) % visibleItems.length;
        openLightbox(currentIndex);
    }

    items.forEach(function (item, index) {
        item.addEventListener('click', function () {
            visibleItems = getVisibleItems();
            currentIndex = visibleItems.indexOf(item);
            openLightbox(currentIndex);
        });
    });

    if (prevBtn) prevBtn.addEventListener('click', showPrev);
    if (nextBtn) nextBtn.addEventListener('click', showNext);

    lightbox.querySelectorAll('[data-close-lightbox]').forEach(function (el) {
        el.addEventListener('click', closeLightbox);
    });

    document.addEventListener('keydown', function (e) {
        if (lightbox.hidden) return;
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowRight') showNext();
        if (e.key === 'ArrowLeft') showPrev();
    });

    filters.forEach(function (filter) {
        filter.addEventListener('click', function () {
            var category = filter.dataset.filter;
            filters.forEach(function (f) { f.classList.remove('is-active'); });
            filter.classList.add('is-active');

            items.forEach(function (item) {
                var match = category === 'all' || item.dataset.category === category;
                item.style.display = match ? '' : 'none';
            });
        });
    });
})();
