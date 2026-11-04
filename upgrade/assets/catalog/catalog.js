/* /catalog/ flipbook: page turning (StPageFlip), hover magnifier, contents + search, deep links (#page/N). */
(function () {
  'use strict';
  var book = document.getElementById('cv-book');
  if (!book) return;
  var pages = Array.prototype.slice.call(book.querySelectorAll('.cv-page'));
  var N = pages.length;
  var $ = function (id) { return document.getElementById(id); };
  var stage = $('cv-stage'), lens = $('cv-lens'), count = $('cv-count'), hint = $('cv-hint');
  var fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var pf = null, state = 'read', current = 0;

  function pageFromHash() {
    var m = /page\/(\d+)/.exec(location.hash);
    var n = m ? parseInt(m[1], 10) : 1;
    return Math.min(Math.max(n, 1), N) - 1;
  }

  // ---------- page turning ----------
  function start() {
    if (!window.St || !St.PageFlip) { book.classList.add('cv-flat'); return; }
    pf = new St.PageFlip(book, {
      width: 566, height: 800, size: 'stretch',
      minWidth: 300, maxWidth: 1131, minHeight: 400, maxHeight: 1600,
      showCover: true, usePortrait: true, autoSize: true,
      maxShadowOpacity: 0.4, flippingTime: reduce ? 1 : 700,
      mobileScrollSupport: true, swipeDistance: 30,
      showPageCorners: false,              // hover belongs to the magnifier
      disableFlipByClick: !fine,           // on phones a tap opens the page full size
      startPage: pageFromHash()
    });
    pf.loadFromHTML(pages);
    pf.on('flip', function (e) { current = e.data; sync(true); });
    pf.on('changeState', function (e) { if (e.data === 'flipping' || e.data === 'user_fold') stage.classList.remove('is-cover'); });
    pf.on('changeState', function (e) { state = e.data; if (state !== 'read') hideLens(); });
    pf.on('changeOrientation', function () { sync(false); });
    current = pf.getCurrentPageIndex();
    sync(false);
  }

  function visibleRange() {
    // the 1-based pages on screen right now
    var i = current;
    if (!pf || pf.getOrientation() === 'portrait') return [i + 1];
    if (i === 0) return [1];                      // the cover sits alone
    var left = i % 2 === 1 ? i : i - 1;           // spreads are (2,3), (4,5) ...
    return left + 1 < N ? [left + 1, left + 2] : [left + 1];
  }

  function sync(fromFlip) {
    var r = visibleRange();
    count.textContent = (r.length > 1 ? r[0] + '–' + r[1] : r[0]) + ' / ' + N;
    stage.classList.toggle('is-cover', !!pf && pf.getOrientation() === 'landscape' && r.length === 1 && r[0] === 1);
    $('cv-prev').disabled = r[0] <= 1;
    $('cv-next').disabled = r[r.length - 1] >= N;
    var thumbs = document.querySelectorAll('.cv-thumb');
    for (var k = 0; k < thumbs.length; k++) {
      var n = +thumbs[k].getAttribute('data-go');
      var on = r.indexOf(n) >= 0;
      thumbs[k].classList.toggle('is-current', on);
      if (on) thumbs[k].setAttribute('aria-current', 'page'); else thumbs[k].removeAttribute('aria-current');
      if (on && n === r[0] && fromFlip) {
        var strip = thumbs[k].closest('.cv-thumbs');
        strip.scrollTo({ left: thumbs[k].offsetLeft - strip.clientWidth / 2 + 35, behavior: reduce ? 'auto' : 'smooth' });
      }
    }
    if (fromFlip) {
      try { history.replaceState(null, '', '#page/' + r[0]); } catch (e) {}
      hint.classList.add('is-off');
    }
  }

  function go(n) {
    var i = Math.min(Math.max(n, 1), N) - 1;
    if (!pf) return;
    var r = visibleRange();
    if (r.indexOf(i + 1) >= 0) return;
    if (Math.abs(i - current) <= 2 && !reduce) pf.flip(i); else { pf.turnToPage(i); current = i; sync(true); }
  }

  $('cv-prev').addEventListener('click', function () { pf && pf.flipPrev(); });
  $('cv-next').addEventListener('click', function () { pf && pf.flipNext(); });
  document.addEventListener('keydown', function (e) {
    if (!pf || e.altKey || e.ctrlKey || e.metaKey) return;
    var t = e.target;
    if (t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable)) return;
    if (!$('cv-zoomview').hidden || !$('cv-drawer').hidden) return;
    if (e.key === 'ArrowRight') { pf.flipNext(); e.preventDefault(); }
    else if (e.key === 'ArrowLeft') { pf.flipPrev(); e.preventDefault(); }
  });
  window.addEventListener('hashchange', function () { go(pageFromHash() + 1); });
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-go]');
    if (!b) return;
    e.preventDefault();
    closeDrawer();
    if (!b.closest('.cv-shell')) $('cv-shell').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    go(+b.getAttribute('data-go'));
  });

  // ---------- hover magnifier ----------
  var ZOOM = 2.6, lensOn = fine, lensPage = null, raf = 0, lastEvt = null, hiLoaded = {};
  var lensBtn = $('cv-lens-t');
  function setLensOn(v) {
    lensOn = v;
    lensBtn.setAttribute('aria-pressed', v ? 'true' : 'false');
    stage.classList.toggle('has-lens', v);
    try { localStorage.setItem('cv-lens', v ? '1' : '0'); } catch (e) {}
    if (!v) hideLens();
  }
  if (fine) {
    try { if (localStorage.getItem('cv-lens') === '0') lensOn = false; } catch (e) {}
    setLensOn(lensOn);
    lensBtn.addEventListener('click', function () { setLensOn(!lensOn); });
  }
  function hideLens() { lens.classList.remove('is-on'); lensPage = null; }
  function pageAt(x, y) {
    var els = document.elementsFromPoint(x, y);
    for (var i = 0; i < els.length; i++) {
      if (els[i] === lens) continue;
      var p = els[i].closest && els[i].closest('.cv-page');
      if (p) return p;
      if (els[i] === stage) return null;
    }
    return null;
  }
  function drawLens() {
    raf = 0;
    var e = lastEvt;
    if (!e || !lensOn || state !== 'read') return hideLens();
    var p = pageAt(e.clientX, e.clientY);
    if (!p) return hideLens();
    var img = p.querySelector('img');
    var r = p.getBoundingClientRect();
    if (r.width < 50) return hideLens();
    var src = img.getAttribute('data-zoom');
    if (!hiLoaded[src]) {
      if (hiLoaded[src] === undefined) {
        hiLoaded[src] = false;
        var pre = new Image();
        pre.onload = function () { hiLoaded[src] = true; if (lastEvt) schedule(lastEvt); };
        pre.src = src;
      }
      src = img.currentSrc || img.src;   // show the sharpest image already loaded meanwhile
    }
    var L = lens.offsetWidth;
    var bw = r.width * ZOOM, bh = r.height * ZOOM;
    var fx = (e.clientX - r.left) / r.width, fy = (e.clientY - r.top) / r.height;
    if (lensPage !== p || lens.getAttribute('data-src') !== src) {
      lens.style.backgroundImage = 'url("' + src + '")';
      lens.setAttribute('data-src', src);
      lensPage = p;
    }
    lens.style.backgroundSize = bw + 'px ' + bh + 'px';
    lens.style.backgroundPosition = (L / 2 - fx * bw) + 'px ' + (L / 2 - fy * bh) + 'px';
    lens.style.left = (e.clientX - L / 2) + 'px';
    lens.style.top = (e.clientY - L / 2) + 'px';
    lens.classList.add('is-on');
  }
  function schedule(e) { lastEvt = e; if (!raf) raf = requestAnimationFrame(drawLens); }
  if (fine) {
    stage.addEventListener('mousemove', schedule);
    stage.addEventListener('mouseleave', function () { lastEvt = null; hideLens(); });
    stage.addEventListener('mousedown', hideLens);
    window.addEventListener('scroll', function () { if (lens.classList.contains('is-on')) hideLens(); }, { passive: true });
  }

  // ---------- full-size page view (phones tap a page; everyone has the zoom button) ----------
  var zv = $('cv-zoomview'), zvImg = $('cv-zv-img'), lastFocus = null;
  function openZoom(n) {
    var p = pages[n - 1];
    if (!p) return;
    var img = p.querySelector('img');
    zvImg.src = img.getAttribute('data-zoom');
    zvImg.alt = img.alt;
    zvImg.classList.remove('is-big');
    lastFocus = document.activeElement;
    zv.hidden = false;
    document.documentElement.style.overflow = 'hidden';
    $('cv-zv-scroll').scrollTo(0, 0);
    $('cv-zv-close').focus();
  }
  function closeZoom() {
    zv.hidden = true;
    document.documentElement.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }
  $('cv-zoom').addEventListener('click', function () { openZoom(visibleRange()[0]); });
  $('cv-zv-close').addEventListener('click', closeZoom);
  zvImg.addEventListener('click', function (e) {
    var sc = $('cv-zv-scroll'), r = zvImg.getBoundingClientRect();
    var fx = (e.clientX - r.left) / r.width, fy = (e.clientY - r.top) / r.height;
    zvImg.classList.toggle('is-big');
    var r2 = zvImg.getBoundingClientRect();
    sc.scrollLeft = fx * r2.width - sc.clientWidth / 2;
    sc.scrollTop = fy * r2.height - sc.clientHeight / 2;
  });
  if (!fine) {
    var down = null;
    stage.addEventListener('pointerdown', function (e) { down = { x: e.clientX, y: e.clientY, t: Date.now() }; });
    stage.addEventListener('pointerup', function (e) {
      if (!down || state !== 'read') return;
      var moved = Math.abs(e.clientX - down.x) + Math.abs(e.clientY - down.y);
      if (moved < 10 && Date.now() - down.t < 400) {
        var p = pageAt(e.clientX, e.clientY);
        if (p) openZoom(+p.getAttribute('data-n'));
      }
      down = null;
    });
  }

  // ---------- full screen ----------
  var shell = $('cv-shell'), fsBtn = $('cv-fs');
  if (!shell.requestFullscreen) fsBtn.hidden = true;
  fsBtn.addEventListener('click', function () {
    if (document.fullscreenElement) document.exitFullscreen(); else shell.requestFullscreen().catch(function () {});
  });

  // ---------- contents drawer + search ----------
  var drawer = $('cv-drawer'), menu = $('cv-menu'), q = $('cv-q'), results = $('cv-results'), toc = $('cv-toc');
  var data = [];
  try { data = JSON.parse($('cv-data').textContent); } catch (e) {}
  function openDrawer() {
    drawer.hidden = false;
    menu.setAttribute('aria-expanded', 'true');
    setTimeout(function () { (fine ? q : $('cv-close')).focus(); }, 30);
  }
  function closeDrawer() {
    if (drawer.hidden) return;
    drawer.hidden = true;
    menu.setAttribute('aria-expanded', 'false');
    menu.focus({ preventScroll: true });
  }
  menu.addEventListener('click', openDrawer);
  $('cv-close').addEventListener('click', closeDrawer);
  drawer.addEventListener('click', function (e) { if (e.target === drawer) closeDrawer(); });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (!zv.hidden) closeZoom(); else closeDrawer();
  });

  function norm(s) { return s.toLowerCase().replace(/[”“″"]/g, '"').replace(/[’‘′]/g, "'").replace(/\s+/g, ' ').trim(); }
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function mark(line, words) {
    var out = esc(line);
    words.forEach(function (w) {
      if (!w) return;
      out = out.replace(new RegExp('(' + esc(w).replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>');
    });
    return out;
  }
  q.addEventListener('input', function () {
    var v = norm(q.value);
    if (v.length < 2) { results.hidden = true; toc.hidden = false; return; }
    var words = v.split(' ');
    var hits = [];
    data.forEach(function (p) {
      var seen = {};
      [p.t].concat(p.l).forEach(function (line) {
        var n = norm(line);
        if (seen[n]) return;
        if (words.every(function (w) { return n.indexOf(w) >= 0; })) { seen[n] = 1; hits.push({ n: p.n, t: p.t, line: line }); }
      });
    });
    results.innerHTML = hits.length
      ? hits.slice(0, 40).map(function (h) {
          return '<li><button type="button" data-go="' + h.n + '"><span>' + mark(h.line, words) + '<small>' + esc(h.t) + '</small></span><span class="cv-toc-n">p.' + h.n + '</span></button></li>';
        }).join('')
      : '<li class="cv-noresult">No match. Try a size like 32oz or a word like napkin.</li>';
    results.hidden = false;
    toc.hidden = true;
  });

  setTimeout(function () { hint.classList.add('is-off'); }, 7000);
  if (!fine) hint.textContent = 'Swipe to turn · tap a page to zoom';

  if (document.readyState === 'complete') start(); else window.addEventListener('load', start);
})();
