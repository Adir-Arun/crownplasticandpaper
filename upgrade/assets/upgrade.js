/* Crown Plastic & Paper: site upgrade layer (behaviour). No dependencies. */
(function () {
  'use strict';
  var EMAIL = 'info@crownplasticandpaper.com';
  var PHONE = '(844) 900-8804';
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- shipping map: draw routes when it scrolls into view ---------- */
  var map = document.querySelector('.cpp-map');
  if (map && 'IntersectionObserver' in window && !reduce) {
    map.classList.add('is-pre');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        requestAnimationFrame(function () { map.classList.add('is-go'); map.classList.remove('is-pre'); });
        io.disconnect();
      });
    }, { threshold: 0.25 });
    io.observe(map);
  }

  /* ---------- mobile quick-contact bar: step aside for the footer and the keyboard ---------- */
  var bar = document.querySelector('.cpp-bar');
  if (bar) {
    var footer = document.querySelector('[data-elementor-type="footer"], footer');
    var footerVisible = false, typing = false;
    var sync = function () { bar.classList.toggle('is-hidden', footerVisible || typing); };
    if (footer && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { footerVisible = es[0].isIntersecting; sync(); }).observe(footer);
    }
    document.addEventListener('focusin', function (e) { if (e.target.matches('input, textarea, select')) { typing = true; sync(); } });
    document.addEventListener('focusout', function () { typing = false; sync(); });
  }

  /* ---------- product search (the WordPress search can't run on a static site) ---------- */
  var index = null, loading = null;
  function loadIndex() {
    if (index) return Promise.resolve(index);
    if (!loading) {
      loading = fetch('/upgrade/search-index.json').then(function (r) { return r.json(); })
        .then(function (d) { index = d; return d; }).catch(function () { index = []; return index; });
    }
    return loading;
  }
  function norm(s) { return (s || '').toLowerCase().normalize('NFKD').replace(/[^\w\s]/g, ' '); }
  function search(q) {
    var terms = norm(q).split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    return index.map(function (it) {
      var name = norm(it.n), all = name + ' ' + norm(it.d) + ' ' + norm(it.k);
      var score = 0;
      for (var i = 0; i < terms.length; i++) {
        var t = terms[i];
        if (all.indexOf(t) < 0 && all.indexOf(t.replace(/s$/, '')) < 0) return null;
        if (name.indexOf(t) === 0) score += 6; else if (name.indexOf(' ' + t) >= 0) score += 4; else if (name.indexOf(t) >= 0) score += 2; else score += 1;
      }
      if (it.k === 'Category') score += 1;
      return { it: it, s: score };
    }).filter(Boolean).sort(function (a, b) { return b.s - a.s || a.it.n.length - b.it.n.length; }).slice(0, 7).map(function (x) { return x.it; });
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

  function enhanceSearch(form) {
    if (form.dataset.cppSearch) return;
    var input = form.querySelector('input[type="search"], input[name="s"]');
    if (!input) return;
    form.dataset.cppSearch = '1';
    form.classList.add('cpp-search');
    var list = document.createElement('div');
    var id = 'cpp-results-' + Math.random().toString(36).slice(2, 8);
    list.className = 'cpp-results'; list.id = id; list.hidden = true; list.setAttribute('role', 'listbox');
    form.appendChild(list);
    input.setAttribute('autocomplete', 'off');
    input.setAttribute('role', 'combobox');
    input.setAttribute('aria-controls', id);
    input.setAttribute('aria-expanded', 'false');
    if (!input.getAttribute('aria-label')) input.setAttribute('aria-label', 'Search products');
    var active = -1, timer;

    function render(items, q) {
      active = -1;
      if (!q.trim()) { list.hidden = true; input.setAttribute('aria-expanded', 'false'); return; }
      list.innerHTML = items.length ? items.map(function (it, i) {
        return '<a role="option" id="' + id + '-' + i + '" aria-selected="false" href="' + esc(it.u) + '">' +
          (it.i ? '<img src="' + esc(it.i) + '" alt="" loading="lazy" decoding="async">' : '<span></span>') +
          '<span><b>' + esc(it.n) + '</b><small>' + esc(it.k) + '</small></span></a>';
      }).join('') : '<div class="cpp-empty">No products match “' + esc(q) + '”. Try another word, or call <a href="tel:+18449008804">' + PHONE + '</a>.</div>';
      list.hidden = false; input.setAttribute('aria-expanded', 'true');
    }
    function move(d) {
      var opts = list.querySelectorAll('[role="option"]'); if (!opts.length) return;
      active = (active + d + opts.length) % opts.length;
      opts.forEach(function (o, i) { o.setAttribute('aria-selected', i === active ? 'true' : 'false'); });
      input.setAttribute('aria-activedescendant', opts[active].id);
      opts[active].scrollIntoView({ block: 'nearest' });
    }
    input.addEventListener('input', function (e) {
      e.stopImmediatePropagation();
      clearTimeout(timer);
      var q = input.value;
      timer = setTimeout(function () { loadIndex().then(function () { render(search(q), q); }); }, 90);
    }, true);
    input.addEventListener('focus', loadIndex);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown') { e.preventDefault(); move(1); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); move(-1); }
      else if (e.key === 'Escape') { list.hidden = true; input.setAttribute('aria-expanded', 'false'); }
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault(); e.stopImmediatePropagation();
      loadIndex().then(function () {
        var opts = list.querySelectorAll('[role="option"]');
        var pick = opts[Math.max(active, 0)];
        if (pick) { location.href = pick.getAttribute('href'); return; }
        render(search(input.value), input.value);
      });
    }, true);
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) { list.hidden = true; input.setAttribute('aria-expanded', 'false'); } });
  }
  function enhanceAllSearch() {
    document.querySelectorAll('form.e-search-form, form[role="search"], form.search-form, form.elementor-search-form').forEach(enhanceSearch);
  }

  /* ---------- forms: WordPress can't receive them here, so hand off to email ---------- */
  function fieldLabel(el) {
    var id = el.id && document.querySelector('label[for="' + el.id + '"]');
    var t = (id && id.textContent) || el.getAttribute('aria-label') || el.placeholder || el.name || '';
    return t.replace(/\*/g, '').trim();
  }
  function note(form, htmlText) {
    var n = form.querySelector('.cpp-form-note');
    if (!n) { n = document.createElement('div'); n.className = 'cpp-form-note'; n.setAttribute('role', 'status'); form.appendChild(n); }
    n.innerHTML = htmlText;
  }
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.matches || !form.matches('form.elementor-form')) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (form.checkValidity && !form.checkValidity()) { form.reportValidity(); return; }
    var lines = [], email = '';
    form.querySelectorAll('input, textarea, select').forEach(function (el) {
      if (['hidden', 'submit', 'button'].indexOf(el.type) >= 0 || !el.value) return;
      if ((el.type === 'checkbox' || el.type === 'radio') && !el.checked) return;
      if (el.type === 'email') email = el.value;
      lines.push(fieldLabel(el) + ': ' + el.value);
    });
    var name = (form.getAttribute('name') || '').toLowerCase();
    var isNewsletter = lines.length <= 1 && email;
    var subject = isNewsletter ? 'Newsletter signup' : (/quote/.test(name + location.pathname) ? 'Quote request' : 'Website inquiry');
    var body = lines.join('\n') + '\n\nSent from ' + location.href;
    var href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    note(form, 'Opening your email app with your message to <a href="mailto:' + EMAIL + '">' + EMAIL + '</a>. ' +
      'Nothing opened? Email us directly or call <a href="tel:+18449008804">' + PHONE + '</a>.');
    window.location.href = href;
  }, true);

  /* ---------- init ---------- */
  function init() { enhanceAllSearch(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  // Elementor renders some widgets late; pick up search forms that appear afterwards.
  window.addEventListener('load', function () { setTimeout(enhanceAllSearch, 400); });
})();
