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
    if (!form.matches || !form.matches('form.elementor-form, form.cpp-quote-form, form.cpp-qq')) return;
    var isQuote = form.classList.contains('cpp-quote-form');
    var isQuick = form.classList.contains('cpp-qq');
    e.preventDefault(); e.stopImmediatePropagation();
    if (form.dataset.cppSending) return;
    if (form.checkValidity && !form.checkValidity()) { form.reportValidity(); return; }

    var data = {}, lines = [], email = '', spam = false;
    if (isQuote) {
      form.querySelectorAll('.cpp-line').forEach(function (row, n) {
        var v = function (sel) { var el = row.querySelector(sel); return el ? el.value.trim() : ''; };
        var product = v('select'), details = v('[name="details"]'), qty = v('[name="qty"]'), unit = v('[name="unit"]');
        if (!product) return;
        var line = product + (details ? ', ' + details : '') + (qty ? ', ' + qty + ' ' + unit.toLowerCase() : '');
        data['Product ' + (n + 1)] = line; lines.push('Product ' + (n + 1) + ': ' + line);
      });
    }
    form.querySelectorAll('input, textarea, select').forEach(function (el) {
      if (['submit', 'button'].indexOf(el.type) >= 0) return;
      if (isQuote && el.closest('.cpp-line')) return;
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
    var subject = isQuick ? 'Quick quote request' : isQuote ? 'Quote request' : isNewsletter ? 'Newsletter signup' : (/quote/.test(name + location.pathname) ? 'Quote request' : 'Website inquiry');
    if (isQuote && data['Company']) subject += ' from ' + data['Company'];
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
    if (isQuote && !lines.length) { note(form, 'Please choose at least one product.', true); return; }

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
          if (isQuick) { note(form, '<strong>Thanks, your request was sent.</strong> Our sales team will email pricing to ' + email + '.'); return; }
          if (isQuote) { resetQuoteLines(form); note(form, '<strong>Thanks, your quote request was sent.</strong> Our sales team will reply to ' + email + ' with pricing.'); return; }
          note(form, isNewsletter ? 'Thanks for subscribing. We\u2019ll send product and inventory updates to ' + email + '.'
            : 'Thanks, your message was sent. Our team will get back to you soon.');
        } else {
          fallback('Your message didn\u2019t send.');
        }
      })
      .catch(function () { clearTimeout(timer); setBusy(false); fallback('The message service didn\u2019t respond.'); });
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

  /* ---------- carousels: load images in carousel slides (lazy-load misses the copies) ---------- */
  function loadCarouselImages() {
    document.querySelectorAll('.swiper img[data-lazy-src], .elementor-loop-container img[data-lazy-src], .e-n-carousel img[data-lazy-src]').forEach(function (img) {
      var src = img.getAttribute('data-lazy-src');
      if (img.getAttribute('data-lazy-srcset')) img.setAttribute('srcset', img.getAttribute('data-lazy-srcset'));
      if (img.getAttribute('data-lazy-sizes')) img.setAttribute('sizes', img.getAttribute('data-lazy-sizes'));
      img.setAttribute('src', src);
      ['data-lazy-src', 'data-lazy-srcset', 'data-lazy-sizes'].forEach(function (a) { img.removeAttribute(a); });
      img.classList.add('entered', 'lazyloaded');
    });
  }

  /* ---------- quote builder (Get Your Quote page) ---------- */
  function resetQuoteLines(form) {
    form.querySelectorAll('.cpp-line').forEach(function (row, i) { if (i) row.remove(); });
    syncLines(form);
  }
  function syncLines(form) {
    var rows = form.querySelectorAll('.cpp-line');
    rows.forEach(function (row, i) {
      var n = i + 1;
      row.querySelectorAll('[id^="cpp-q-"]').forEach(function (el) {
        var base = el.id.replace(/-\d+$/, '');
        var lab = row.querySelector('label[for="' + el.id + '"]');
        el.id = base + '-' + n; if (lab) lab.setAttribute('for', el.id);
      });
      var rm = row.querySelector('.cpp-line-remove');
      rm.hidden = rows.length < 2;
      rm.setAttribute('aria-label', 'Remove product ' + n);
    });
  }
  function fillProducts(select, items) {
    if (select.dataset.cppFilled) return;
    select.dataset.cppFilled = '1';
    items.forEach(function (it) { var o = document.createElement('option'); o.textContent = it.n; select.appendChild(o); });
    var other = document.createElement('option'); other.textContent = 'Something else (describe in details)'; select.appendChild(other);
  }
  function choose(select, name) {
    if (!name) return;
    var want = name.toLowerCase().trim(), hit = null;
    Array.prototype.forEach.call(select.options, function (o) { if (!hit && o.value.toLowerCase() === want) hit = o; });
    if (!hit) { hit = document.createElement('option'); hit.textContent = name; select.insertBefore(hit, select.options[1] || null); }
    select.value = hit.value;
  }
  function initQuote() {
    var form = document.querySelector('form.cpp-quote-form');
    if (!form) return;
    var tpl = form.querySelector('.cpp-line').cloneNode(true);
    var params = new URLSearchParams(location.search);
    loadIndex().then(function (all) {
      var items = all.filter(function (x) { return x.k === 'Product'; });
      if (!items.length) throw new Error('no products');
      form._cppItems = items;
      form.querySelectorAll('select[data-cpp-products]').forEach(function (sel) { fillProducts(sel, items); });
      var first = form.querySelector('.cpp-line');
      choose(first.querySelector('select'), params.get('product'));
      if (params.get('details')) first.querySelector('[name="details"]').value = params.get('details');
    }).catch(function () {
      // No product list: let people type the product instead.
      form.querySelectorAll('select[data-cpp-products]').forEach(function (sel) {
        var inp = document.createElement('input'); inp.type = 'text'; inp.id = sel.id; inp.name = 'product'; inp.required = true;
        inp.value = params.get('product') || ''; sel.replaceWith(inp);
      });
    });
    var lastAdd = 0;
    form.querySelector('.cpp-add-line').addEventListener('click', function (e) {
      // WP Rocket replays clicks as synthetic events; one press adds one row.
      if (!e.isTrusted && Date.now() - lastAdd < 400) return;
      lastAdd = Date.now();
      var row = tpl.cloneNode(true);
      row.querySelectorAll('input').forEach(function (i) { i.value = ''; });
      var sel = row.querySelector('select[data-cpp-products]');
      sel.removeAttribute('data-cpp-filled'); sel.required = false;
      if (form._cppItems) fillProducts(sel, form._cppItems);
      form.querySelector('.cpp-lines').appendChild(row);
      syncLines(form);
      sel.focus();
    });
    form.addEventListener('click', function (e) {
      var rm = e.target.closest('.cpp-line-remove');
      if (!rm || !rm.isConnected || !rm.closest('.cpp-line')) return;
      var row = rm.closest('.cpp-line'), prev = row.previousElementSibling || row.nextElementSibling;
      row.remove(); syncLines(form);
      if (prev) prev.querySelector('select, input').focus();
    });
  }

  /* ---------- product page: "Price Upon Request" opens the quote form for this product ---------- */
  function productName() {
    var t = document.querySelector('h1.product_title, .product_title');
    return t ? t.textContent.trim() : '';
  }
  function productQuoteUrl() {
    var details = [];
    document.querySelectorAll('table.variations select').forEach(function (sel) {
      if (!sel.value) return;
      var lab = sel.id && document.querySelector('table.variations label[for="' + sel.id + '"]');
      details.push((lab ? lab.textContent.trim() + ' ' : '') + sel.options[sel.selectedIndex].text.trim());
    });
    var q = '?product=' + encodeURIComponent(productName());
    if (details.length) q += '&details=' + encodeURIComponent(details.join(', '));
    return '/get-your-quote/' + q;
  }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('#product-detail-quote, [data-cpp-product-quote]');
    if (!btn || !productName()) return;
    e.preventDefault();
    location.href = productQuoteUrl();
  }, true);
  /* mobile quick bar: on a product page the quote button names the product */
  function initProductBar() {
    var name = productName();
    var a = document.querySelector('.cpp-bar a[href*="get-your-quote"]');
    if (!name || !a || !/^\/product\//.test(location.pathname)) return;
    a.setAttribute('data-cpp-product-quote', '');
    a.setAttribute('aria-label', 'Request a quote for ' + name);
    var label = [].filter.call(a.childNodes, function (n) { return n.nodeType === 3 && n.textContent.trim(); })[0];
    var span = document.createElement('span'); span.className = 'cpp-bar-label'; span.textContent = 'Quote ' + name;
    if (label) label.replaceWith(span); else a.appendChild(span);
  }

  /* ---------- homepage: quick quote suggestions, clickable customer tiles, contact card ---------- */
  function initHome() {
    var list = document.getElementById('cpp-qq-list');
    if (list) loadIndex().then(function (all) {
      all.filter(function (x) { return x.k === 'Product'; }).forEach(function (x) { var o = document.createElement('option'); o.value = x.n; list.appendChild(o); });
    });
    var targets = { 'Wholesalers': '/products/', 'Food Distributors': '/products/', 'Cash and Carry': '/products/',
      'Hospitals': '/products/product_cat-gloves/', 'Schools': '/product/school-trays/',
      'Chain Restaurants': '/products/product_cat-food-service-supplies/', 'Catering Services': '/products/product_cat-food-service-supplies/',
      'More Businesses': '/products/' };
    document.querySelectorAll('.arus-our-services .elementor-image-box-title').forEach(function (t) {
      var name = t.textContent.trim(), href = targets[name];
      var box = t.closest('.elementor-widget-image-box') || t.closest('.elementor-widget');
      if (!href || !box || box.querySelector('.cpp-tile-link')) return;
      var a = document.createElement('a'); a.className = 'cpp-tile-link'; a.href = href;
      a.setAttribute('aria-label', name + ': see products');
      box.classList.add('cpp-tile-host'); box.appendChild(a);
    });
    var ci = [].find.call(document.querySelectorAll('.elementor-heading-title'), function (h) { return h.textContent.trim() === 'Contact Info'; });
    var card = ci && ci.closest('.e-con');
    if (card && !card.querySelector('.cpp-cardx')) {
      var x = document.createElement('div'); x.className = 'cpp-cardx';
      x.innerHTML = '<p>Need pricing for a full supply list?</p>' +
        '<a class="cpp-btn cpp-btn--solid" href="/get-your-quote/">Request a Quote<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg></a>' +
        '<a class="cpp-btn cpp-btn--line" href="https://heyzine.com/flip-book/0ee04dad9c.html#page/13" target="_blank" rel="noopener">View 2026 Catalog</a>';
      card.appendChild(x);
    }
  }

  /* desktop: a slim bar keeps navigation and the quote button in reach once the header scrolls away */
  function initStickyBar() {
    var header = document.querySelector('[data-elementor-type="header"]');
    if (!header || !('IntersectionObserver' in window)) return;
    var name = /^\/product\//.test(location.pathname) ? productName() : '';
    var bar = document.createElement('div');
    bar.className = 'cpp-sticky'; bar.setAttribute('aria-hidden', 'true');
    bar.innerHTML = '<div class="cpp-sticky-in">' +
      '<a class="cpp-sticky-logo" href="/" tabindex="-1"><img src="/wp-content/uploads/2026/01/icn_crown_logo.svg" width="44" height="40" alt="Crown Plastic &amp; Paper home"></a>' +
      '<nav class="cpp-sticky-nav" aria-label="Quick navigation">' +
        '<a href="/products/" tabindex="-1">Products</a><a href="/products/product_cat-gloves/" tabindex="-1">Disposable Gloves</a>' +
        '<a href="https://heyzine.com/flip-book/0ee04dad9c.html#page/13" target="_blank" rel="noopener" tabindex="-1">Catalog</a>' +
        '<a href="/about-us/" tabindex="-1">About Us</a><a href="/contact-us/" tabindex="-1">Contact</a></nav>' +
      '<a class="cpp-sticky-tel" href="tel:+18449008804" tabindex="-1">' + PHONE + '</a>' +
      '<a class="cpp-sticky-cta" href="/get-your-quote/" tabindex="-1"' + (name ? ' data-cpp-product-quote' : '') + '>' +
        (name ? '<span>Quote ' + name.replace(/[<&]/g, '') + '</span>' : 'Get a Quote') + '</a></div>';
    document.body.appendChild(bar);
    var links = bar.querySelectorAll('a');
    new IntersectionObserver(function (es) {
      var show = !es[0].isIntersecting && window.innerWidth > 1024;
      bar.classList.toggle('is-on', show);
      bar.setAttribute('aria-hidden', show ? 'false' : 'true');
      links.forEach(function (l) { if (show) l.removeAttribute('tabindex'); else l.setAttribute('tabindex', '-1'); });
    }, { rootMargin: '0px' }).observe(header);
  }
  function initQuoteButton() {
    var a = document.getElementById('product-detail-quote');
    if (a && !a.getAttribute('href')) a.setAttribute('href', '/get-your-quote/');
  }

  /* ---------- product page: printable spec sheet ---------- */
  function initSpecPrint() {
    if (!/^\/product\//.test(location.pathname)) return;
    var h = Array.prototype.find.call(document.querySelectorAll('.elementor-heading-title'), function (x) { return x.textContent.trim() === 'Specifications'; });
    if (!h) return;
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'cpp-print';
    b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 9V3h10v6M7 17H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2M7 14h10v7H7z"/></svg>Print Spec Sheet';
    b.addEventListener('click', function () { window.print(); });
    var widget = h.closest('.elementor-widget');
    widget.classList.add('cpp-has-print');
    widget.appendChild(b);
    var ph = document.createElement('div');
    ph.className = 'cpp-print-head';
    ph.innerHTML = '<strong>Crown Plastic &amp; Paper</strong><span>' + PHONE + ' · ' + EMAIL + ' · crownplasticandpaper.com</span>';
    document.body.insertBefore(ph, document.body.firstChild);
  }

  /* ---------- back to top ---------- */
  function initToTop() {
    var b = document.createElement('button');
    b.type = 'button'; b.className = 'cpp-totop'; b.setAttribute('aria-label', 'Back to top');
    b.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
    b.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' });
      var skip = document.getElementById('content'); if (skip) skip.focus({ preventScroll: true });
    });
    document.body.appendChild(b);
    var ticking = false;
    window.addEventListener('scroll', function () {
      if (ticking) return; ticking = true;
      requestAnimationFrame(function () { b.classList.toggle('is-on', window.scrollY > window.innerHeight * 1.5); ticking = false; });
    }, { passive: true });
  }

  /* ---------- blog posts: reading time and progress ---------- */
  function initArticle() {
    if (!document.body.classList.contains('single-post')) return;
    var body = document.querySelector('.elementor-widget-theme-post-content');
    if (!body) return;
    var words = (body.textContent || '').trim().split(/\s+/).length;
    var mins = Math.max(1, Math.round(words / 225));
    var info = document.querySelector('ul.elementor-post-info');
    if (info) {
      var li = document.createElement('li');
      li.className = 'elementor-icon-list-item elementor-inline-item cpp-readtime';
      li.innerHTML = '<span class="elementor-icon-list-icon"><svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg></span><span class="elementor-icon-list-text">' + mins + ' min read</span>';
      info.appendChild(li);
    }
    var bar = document.createElement('div');
    bar.className = 'cpp-progress'; bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);
    var update = function () {
      var r = body.getBoundingClientRect();
      var total = r.height - window.innerHeight * 0.6;
      var p = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 1;
      bar.style.transform = 'scaleX(' + p.toFixed(4) + ')';
    };
    window.addEventListener('scroll', function () { requestAnimationFrame(update); }, { passive: true });
    update();
  }

  /* ---------- init ---------- */
  var started = false;
  function init() {
    enhanceAllSearch(); enhanceFields();
    if (started) return;  // WP Rocket re-fires DOMContentLoaded; set these up once
    started = true;
    [initQuote, initQuoteButton, initSpecPrint, initToTop, initArticle, initProductBar, initStickyBar, initHome].forEach(function (f) { try { f(); } catch (err) { if (window.console) console.warn('cpp', err); } });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  // Elementor renders some widgets late; pick up search forms that appear afterwards.
  window.addEventListener('load', function () {
    setTimeout(function () { enhanceAllSearch(); loadCarouselImages(); }, 400);
    setTimeout(loadCarouselImages, 1800);  // carousels add their slide copies after start-up
  });
})();
