/**
 * Auto-advance horizontal gallery strips marked with [data-gallery-scroll].
 * Pauses on hover / touch. Skips single-image or non-overflowing tracks.
 */
(function () {
  var DEFAULT_INTERVAL_MS = 3000;
  var DEFAULT_GAP_PX = 32;

  function readGap(scrollEl) {
    var row = scrollEl.querySelector('.gallery-scroll-row') || scrollEl.firstElementChild;
    if (!row) return DEFAULT_GAP_PX;
    var styles = window.getComputedStyle(row);
    var gap = parseFloat(styles.columnGap || styles.gap || '');
    return Number.isFinite(gap) ? gap : DEFAULT_GAP_PX;
  }

  function canScroll(scrollEl) {
    return scrollEl.scrollWidth - scrollEl.clientWidth > 2;
  }

  function initGalleryScroll(scrollEl) {
    if (!scrollEl || scrollEl.dataset.galleryAutoscroll === 'off') return;
    if (scrollEl.__galleryAutoScrollInit) return;

    var cards = scrollEl.querySelectorAll('[data-gallery-card]');
    if (cards.length <= 1 || !canScroll(scrollEl)) return;

    scrollEl.__galleryAutoScrollInit = true;
    var paused = false;
    var intervalMs = parseInt(scrollEl.getAttribute('data-gallery-interval'), 10);
    if (!Number.isFinite(intervalMs) || intervalMs < 1000) {
      intervalMs = DEFAULT_INTERVAL_MS;
    }

    scrollEl.addEventListener('mouseenter', function () { paused = true; });
    scrollEl.addEventListener('mouseleave', function () { paused = false; });
    scrollEl.addEventListener('focusin', function () { paused = true; });
    scrollEl.addEventListener('focusout', function () { paused = false; });
    scrollEl.addEventListener('touchstart', function () { paused = true; }, { passive: true });
    scrollEl.addEventListener('touchend', function () {
      window.setTimeout(function () { paused = false; }, 2500);
    }, { passive: true });

    function advance() {
      if (paused || !canScroll(scrollEl)) return;
      var card = scrollEl.querySelector('[data-gallery-card]');
      var step = card ? card.offsetWidth + readGap(scrollEl) : 412;
      var maxScroll = scrollEl.scrollWidth - scrollEl.clientWidth;
      scrollEl.scrollLeft += step;
      if (scrollEl.scrollLeft >= maxScroll - 2) {
        scrollEl.scrollLeft = 0;
      }
    }

    window.setInterval(advance, intervalMs);
  }

  function initAll() {
    document.querySelectorAll('[data-gallery-scroll]').forEach(initGalleryScroll);
  }

  function scheduleInit() {
    window.setTimeout(initAll, 300);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleInit);
  } else {
    scheduleInit();
  }
  window.addEventListener('load', initAll);
})();
