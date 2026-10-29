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

  /* ---------- forms: delivered by FormSubmit (formsubmit.co) to the sales inbox ---------- */
  var FORM_ENDPOINT = 'https://formsubmit.co/ajax/' + EMAIL;
  function fieldLabel(el) {
    var id = el.id && document.querySelector('label[for="' + el.id + '"]');
    var t = (id && id.textContent) || el.getAttribute('aria-label') || el.placeholder || el.name || 'Field';
    return t.replace(/\*/g, '').trim();
  }
  function note(form, htmlText, isError) {
    var n = form.querySelector('.cpp-form-note');
    if (!n) { n = document.createElement('div'); n.className = 'cpp-form-note'; form.appendChild(n); }
    n.setAttribute('role', isError ? 'alert' : 'status');
    n.classList.toggle('is-error', !!isError);
    n.innerHTML = htmlText;
  }
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form.matches || !form.matches('form.elementor-form')) return;
    e.preventDefault(); e.stopImmediatePropagation();
    if (form.dataset.cppSending) return;
    if (form.checkValidity && !form.checkValidity()) { form.reportValidity(); return; }

    var data = {}, lines = [], email = '', spam = false;
    form.querySelectorAll('input, textarea, select').forEach(function (el) {
      if (['submit', 'button'].indexOf(el.type) >= 0) return;
      if (/honey/i.test(el.name || '')) { if (el.value) spam = true; return; }
      if (el.type === 'hidden' || !el.value) return;
      if ((el.type === 'checkbox' || el.type === 'radio') && !el.checked) return;
      if (el.type === 'email') email = el.value;
      var label = fieldLabel(el), key = label, i = 2;
      while (data[key] !== undefined) key = label + ' ' + i++;
      data[key] = el.value; lines.push(label + ': ' + el.value);
    });
    var name = (form.getAttribute('name') || '').toLowerCase();
    var isNewsletter = lines.length <= 1 && !!email;
    var subject = isNewsletter ? 'Newsletter signup' : (/quote/.test(name + location.pathname) ? 'Quote request' : 'Website inquiry');
    var page = document.title.split('|')[0].trim();
    data._subject = subject + ' - crownplasticandpaper.com';
    data._template = 'table';
    data._captcha = 'false';
    if (email) data._replyto = email;
    data['Sent from'] = location.href.split('#')[0];

    var btn = form.querySelector('[type="submit"]');
    var btnText = btn && btn.querySelector('.elementor-button-text');
    var original = btnText ? btnText.textContent : (btn && btn.textContent);
    function setBusy(on) {
      if (on) form.dataset.cppSending = '1'; else delete form.dataset.cppSending;
      if (!btn) return;
      btn.disabled = on; btn.setAttribute('aria-busy', on ? 'true' : 'false');
      if (btnText) btnText.textContent = on ? 'Sending…' : original;
    }
    function fallback(reason) {
      var href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(lines.join('\n') + '\n\nSent from ' + location.href);
      note(form, reason + ' Please <a href="' + href + '">email your message</a> instead, or call <a href="tel:+18449008804">' + PHONE + '</a>.', true);
    }
    if (spam) { form.reset(); note(form, 'Thanks, your message was sent.'); return; }

    setBusy(true);
    var ctrl = 'AbortController' in window ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, 15000);
    fetch(FORM_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: JSON.stringify(data),
      signal: ctrl ? ctrl.signal : undefined
    }).then(function (r) { return r.json().catch(function () { return {}; }); })
      .then(function (res) {
        clearTimeout(timer); setBusy(false);
        if (res && (res.success === true || res.success === 'true')) {
          form.reset();
          note(form, isNewsletter ? 'Thanks for subscribing. We\u2019ll send product and inventory updates to ' + email + '.'
            : 'Thanks, your message was sent. Our team will get back to you soon.');
        } else {
          fallback('We couldn\u2019t send your message right now.');
        }
      })
      .catch(function () { clearTimeout(timer); setBusy(false); fallback('We couldn\u2019t reach our message service.'); });
  }, true);

  /* ---------- form fields: right keyboard and autofill ---------- */
  function enhanceFields() {
    document.querySelectorAll('form.elementor-form input, form.elementor-form textarea').forEach(function (el) {
      var hint = ((el.placeholder || '') + ' ' + fieldLabel(el) + ' ' + (el.name || '')).toLowerCase();
      if (/phone|tel/.test(hint)) {
        if (el.type === 'number') el.type = 'tel';
        el.setAttribute('inputmode', 'tel'); el.setAttribute('autocomplete', 'tel');
      } else if (el.type === 'email') el.setAttribute('autocomplete', 'email');
      else if (/company|business/.test(hint)) el.setAttribute('autocomplete', 'organization');
      else if (/full name|your name|^\s*name|\[name\]/.test(hint)) el.setAttribute('autocomplete', 'name');
      if (!el.getAttribute('aria-label') && el.placeholder && !(el.id && document.querySelector('label[for="' + el.id + '"]'))) el.setAttribute('aria-label', el.placeholder);
    });
  }

  /* ---------- init ---------- */
  function init() { enhanceAllSearch(); enhanceFields(); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  // Elementor renders some widgets late; pick up search forms that appear afterwards.
  window.addEventListener('load', function () { setTimeout(enhanceAllSearch, 400); });
})();
