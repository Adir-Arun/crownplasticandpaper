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
  // Web3Forms is the primary delivery path once its access key (public by design) is set;
  // FormSubmit stays as the automatic backup.
  var W3F_KEY = 'ccf6d55e-e535-42d9-acd7-f01ec08d8e8a';
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
    // If the form service is unreachable, keep the visitor on our page and hand them the
    // finished request as one-tap email / WhatsApp / text, so no request is lost.
    function fallback() {
      var text = subject + '\n\n' + lines.join('\n');
      var mail = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text + '\n\nSent from ' + location.href);
      var wa = 'https://wa.me/17136975320?text=' + encodeURIComponent(text);
      var sms = 'sms:+17136975320?&body=' + encodeURIComponent(text);
      note(form, '<strong>Our online form isn\u2019t responding right now.</strong> Your request is ready \u2014 send it with one tap:' +
        '<span class="cpp-fb-actions">' +
        '<a class="cpp-fb-btn cpp-fb-btn--main" href="' + mail + '">Email it</a>' +
        '<a class="cpp-fb-btn" href="' + wa + '" target="_blank" rel="noopener">WhatsApp</a>' +
        '<a class="cpp-fb-btn" href="' + sms + '">Text</a>' +
        '<button type="submit" class="cpp-fb-btn cpp-fb-retry">Try again</button></span>' +
        '<span class="cpp-fb-call">Or call <a href="tel:+18449008804">' + PHONE + '</a></span>', true);
    }
    if (spam) { form.reset(); note(form, 'Thanks, your message was sent.'); return; }
    if (isQuote && !lines.length) { note(form, 'Please choose at least one product.', true); return; }

    setBusy(true);
    function done(res) {
      setBusy(false);
      form.reset();
      if (isQuick) { note(form, '<strong>Thanks, your request was sent.</strong> Our sales team will email pricing to ' + email + '.'); return; }
      if (isQuote) { resetQuoteLines(form); note(form, '<strong>Thanks, your quote request was sent.</strong> Our sales team will reply to ' + email + ' with pricing.'); return; }
      note(form, isNewsletter ? 'Thanks for subscribing. We\u2019ll send product and inventory updates to ' + email + '.'
        : 'Thanks, your message was sent. Our team will get back to you soon.');
    }
    function post(url, opts, ms) {
      var ctrl = 'AbortController' in window ? new AbortController() : null;
      var timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, ms);
      opts.signal = ctrl ? ctrl.signal : undefined;
      return fetch(url, opts).then(function (r) { clearTimeout(timer); return r.json().catch(function () { return {}; }); },
                                   function (err) { clearTimeout(timer); throw err; });
    }
    function viaFormSubmit() {
      // Plain form encoding: a "simple" request, so the browser sends it without a CORS preflight
      var body = new URLSearchParams();
      Object.keys(data).forEach(function (k) { body.append(k, data[k]); });
      return post(FORM_ENDPOINT, { method: 'POST', headers: { 'Accept': 'application/json' }, body: body }, 12000)
        .then(function (res) {
          if (res && (res.success === true || res.success === 'true')) return done(res);
          if (res && /activat/i.test(res.message || '')) {
            setBusy(false);
            note(form, 'Thanks, your message was received. It will be delivered as soon as the inbox is confirmed. For anything urgent call <a href="tel:+18449008804">' + PHONE + '</a>.');
            return;
          }
          throw new Error('formsubmit');
        });
    }
    function viaWeb3Forms() {
      var payload = { access_key: W3F_KEY, subject: data._subject, from_name: 'Crown website' };
      if (email) payload.replyto = email;
      Object.keys(data).forEach(function (k) { if (k.charAt(0) !== '_') payload[k] = data[k]; });
      return post('https://api.web3forms.com/submit', {
        method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(payload)
      }, 12000).then(function (res) { if (res && res.success) return done(res); throw new Error('web3forms'); });
    }
    (W3F_KEY ? viaWeb3Forms().catch(viaFormSubmit) : viaFormSubmit())
      .catch(function () { setBusy(false); fallback(); });
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
    if (name && /^\/product\//.test(location.pathname)) document.querySelectorAll('a[href^="https://wa.me/"]').forEach(function (w) {
      w.href = w.href.split('?')[0] + '?text=' + encodeURIComponent('Hi Crown, I\'d like a quote for ' + name + ': ');
    });
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
        '<a class="cpp-btn cpp-btn--line" href="https://heyzine.com/flip-book/0ee04dad9c.html#page/13" target="_blank" rel="noopener">View 2026 Catalog</a>' +
        '<p class="cpp-cardx-text">Prefer to text? <a href="sms:+17136975320">(713) 697-5320</a> · <a href="https://wa.me/17136975320?text=Hi%20Crown%2C%20I%27d%20like%20a%20quote%20for%3A%20" target="_blank" rel="noopener">WhatsApp</a></p>';
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
      '<a class="cpp-sticky-wa" href="https://wa.me/17136975320?text=Hi%20Crown%2C%20I%27d%20like%20a%20quote%20for%3A%20" target="_blank" rel="noopener" tabindex="-1">WhatsApp</a>' +
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

  /* ---------- category filter: update the list in place instead of loading a new page ---------- */
  function initFilterNav() {
    var section = document.querySelector('.wpc-filters-section.wpc-filter-product_cat');
    if (!section || !window.fetch || !window.DOMParser || !history.pushState) return;
    var cache = {};
    function linkFor(item) {
      var input = item && item.querySelector('input[data-wpc-link]');
      return input ? input.getAttribute('data-wpc-link') : null;
    }
    function get(url) {
      if (!cache[url]) cache[url] = fetch(url, { credentials: 'same-origin' }).then(function (r) {
        if (!r.ok) throw new Error(r.status); return r.text();
      });
      return cache[url];
    }
    function wakeImages(root) {
      root.querySelectorAll('img[data-lazy-src]').forEach(function (img) {
        img.src = img.getAttribute('data-lazy-src');
        if (img.getAttribute('data-lazy-srcset')) img.srcset = img.getAttribute('data-lazy-srcset');
      });
    }
    var busy = false;
    function go(url, push, focusId) {
      var wrap = document.querySelector('.woocommerce-products-wrapper');
      if (!wrap || busy) { location.href = url; return; }
      busy = true; wrap.classList.add('cpp-loading'); wrap.setAttribute('aria-busy', 'true');
      get(url).then(function (htmlText) {
        var doc = new DOMParser().parseFromString(htmlText, 'text/html');
        var newWrap = doc.querySelector('.woocommerce-products-wrapper');
        var newSection = doc.querySelector('.wpc-filters-section.wpc-filter-product_cat');
        if (!newWrap || !newSection) throw new Error('layout');
        wrap.innerHTML = newWrap.innerHTML; wakeImages(wrap);
        var cur = document.querySelector('.wpc-filters-section.wpc-filter-product_cat');
        cur.innerHTML = newSection.innerHTML;
        var hero = document.querySelector('.cpp-cat-hero'), newHero = doc.querySelector('.cpp-cat-hero');
        if (hero && newHero) hero.outerHTML = newHero.outerHTML;
        else if (hero) hero.remove();
        else if (newHero) { var content = document.getElementById('content'); if (content) content.insertAdjacentHTML('afterbegin', newHero.outerHTML); }
        document.title = doc.title;
        if (push) history.pushState({ cppFilter: true }, '', url);
        if (focusId) { var f = document.getElementById(focusId); if (f) f.focus({ preventScroll: true }); }
        var top = wrap.getBoundingClientRect().top;
        if (top < 0) window.scrollBy({ top: top - 90, behavior: 'smooth' });
      }).catch(function () { location.href = url; })
        .then(function () { busy = false; wrap.classList.remove('cpp-loading'); wrap.removeAttribute('aria-busy'); });
    }
    document.addEventListener('click', function (e) {
      var item = e.target.closest && e.target.closest('.wpc-filter-product_cat .wpc-term-item');
      if (!item) return;
      var url = linkFor(item);
      if (!url) return;
      e.preventDefault(); e.stopImmediatePropagation();
      var input = item.querySelector('input');
      go(url, true, input && input.id);
    }, true);
    // warm the cache so the switch feels instant
    ['pointerenter', 'touchstart', 'focusin'].forEach(function (ev) {
      document.addEventListener(ev, function (e) {
        var item = e.target.closest && e.target.closest('.wpc-filter-product_cat .wpc-term-item');
        var url = linkFor(item);
        if (url) get(url).catch(function () { delete cache[url]; });
      }, { capture: true, passive: true });
    });
    history.replaceState({ cppFilter: true }, '', location.href);
    window.addEventListener('popstate', function (e) { if (e.state && e.state.cppFilter) go(location.pathname, false); });
  }

  /* ---------- credit application (Fluent Forms): its WordPress endpoint is gone, deliver it ourselves ---------- */
  function initFluentForms() {
    var forms = document.querySelectorAll('form.frm-fluent-form');
    if (!forms.length) return;
    var MAX_FILE = 5 * 1024 * 1024;
    function groupLabel(g) {
      var l = g.querySelector('.ff-el-input--label label, .ff-el-input--label');
      return l ? l.textContent.replace(/\*/g, '').replace(/\s+/g, ' ').trim() : '';
    }
    forms.forEach(function (form) {
      // The plugin uploads files the moment they are picked, to an endpoint that no longer exists:
      // keep the file in the form and show its name instead.
      form.querySelectorAll('input[type="file"]').forEach(function (inp) {
        inp.removeAttribute('multiple');
        var out = document.createElement('div'); out.className = 'cpp-ff-files'; out.setAttribute('aria-live', 'polite');
        (inp.closest('.ff-el-input--content') || inp.parentNode).appendChild(out);
        inp.addEventListener('change', function (e) {
          e.stopImmediatePropagation();
          var f = inp.files && inp.files[0];
          out.textContent = f ? 'Attached: ' + f.name + ' (' + Math.max(1, Math.round(f.size / 1024)) + ' KB)' + (f.size > MAX_FILE ? ' — over 5 MB, please email it instead' : '') : '';
        }, true);
      });
    });
    document.addEventListener('submit', function (e) {
      var form = e.target;
      if (!form.matches || !form.matches('form.frm-fluent-form')) return;
      e.preventDefault(); e.stopImmediatePropagation();
      if (form.dataset.cppSending) return;
      // required fields (the plugin marks them with aria-required, not "required")
      var missing = null;
      form.querySelectorAll('[aria-required="true"]').forEach(function (el) {
        var empty = (el.type === 'checkbox') ? !form.querySelector('[name="' + el.name + '"]:checked') : !String(el.value || '').trim();
        el.classList.toggle('cpp-ff-missing', empty);
        if (empty && !missing) missing = el;
      });
      if (missing) { missing.focus(); note(form, 'Please fill in the highlighted required fields.', true); return; }
      var fields = {}, lines = [], email = '', company = '', files = [];
      form.querySelectorAll('.ff-el-group').forEach(function (g) {
        if (g.querySelector('.ff-el-group')) return;  // only innermost groups
        var label = groupLabel(g);
        var vals = [];
        g.querySelectorAll('input, select, textarea').forEach(function (el) {
          if (el.type === 'hidden' || el.type === 'submit' || el.type === 'button') return;
          if (el.type === 'file') return;
          if ((el.type === 'checkbox' || el.type === 'radio') && !el.checked) return;
          var v = String(el.value || '').trim(); if (!v) return;
          if (el.tagName === 'SELECT' && el.selectedIndex > -1) v = el.options[el.selectedIndex].text.trim();
          if (el.type === 'email' && !email) email = v;
          if (el.name === 'company_name') company = v;
          if (el.name === 'terms-n-condition') v = 'Agreed';
          vals.push(v);
        });
        if (!vals.length) return;
        var key = label || 'Field', i = 2; while (fields[key] !== undefined) key = (label || 'Field') + ' ' + i++;
        fields[key] = vals.join(', '); lines.push(key + ': ' + fields[key]);
      });
      form.querySelectorAll('input[type="file"]').forEach(function (inp) { if (inp.files) for (var k = 0; k < inp.files.length; k++) files.push(inp.files[k]); });
      if (files.length) { fields['Attached documents'] = files.map(function (f) { return f.name; }).join(', '); lines.push('Attached documents: ' + fields['Attached documents']); }
      var subject = 'Credit application' + (company ? ' from ' + company : '');
      fields['Sent from'] = location.href.split('#')[0];
      var btn = form.querySelector('[type="submit"]'), btnLabel = btn ? btn.innerHTML : '';
      function busy(on) { if (on) form.dataset.cppSending = '1'; else delete form.dataset.cppSending; if (btn) { btn.disabled = on; btn.innerHTML = on ? 'Sending…' : btnLabel; } }
      function build(withFiles) {
        var fd = new FormData();
        fd.append('access_key', W3F_KEY); fd.append('subject', subject + ' - crownplasticandpaper.com'); fd.append('from_name', 'Crown website');
        if (email) fd.append('replyto', email);
        Object.keys(fields).forEach(function (k) { fd.append(k, fields[k]); });
        if (withFiles) files.forEach(function (f, n) { if (f.size <= MAX_FILE) fd.append(n ? 'attachment_' + (n + 1) : 'attachment', f, f.name); });
        return fd;
      }
      function send(fd) {
        var ctrl = 'AbortController' in window ? new AbortController() : null;
        var t = setTimeout(function () { if (ctrl) ctrl.abort(); }, 45000);
        return fetch('https://api.web3forms.com/submit', { method: 'POST', body: fd, signal: ctrl ? ctrl.signal : undefined })
          .then(function (r) { clearTimeout(t); return r.json().catch(function () { return {}; }); }, function (err) { clearTimeout(t); throw err; })
          .then(function (res) { if (!res || !res.success) throw new Error((res && res.message) || 'failed'); return res; });
      }
      var mailDocs = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent('Documents for ' + subject) + '&body=' + encodeURIComponent('Attached are the documents for our credit application.\n\n' + (company ? 'Company: ' + company + '\n' : '') + (email ? 'Email: ' + email : ''));
      busy(true);
      var hadFiles = files.some(function (f) { return f.size <= MAX_FILE; });
      var tooBig = files.some(function (f) { return f.size > MAX_FILE; });
      (hadFiles ? send(build(true)).then(function () { return true; }, function () { return send(build(false)).then(function () { return false; }); })
                : send(build(false)).then(function () { return !files.length; }))
        .then(function (filesDelivered) {
          busy(false); form.reset(); form.querySelectorAll('.cpp-ff-files').forEach(function (o) { o.textContent = ''; });
          var msg = '<strong>Thanks, your credit application was sent.</strong> Our team will review it and contact you' + (email ? ' at ' + email : '') + '.';
          if (files.length && (!filesDelivered || tooBig)) msg += ' To complete it, please <a href="' + mailDocs + '">email your documents</a> to ' + EMAIL + '.';
          note(form, msg);
          form.querySelector('.cpp-form-note').scrollIntoView({ behavior: 'smooth', block: 'center' });
        })
        .catch(function () {
          busy(false);
          var text = subject + '\n\n' + lines.join('\n');
          note(form, '<strong>Our online form isn’t responding right now.</strong> Your application is ready — ' +
            '<a href="mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(text) + '">email it with one tap</a>' +
            (files.length ? ' and attach your documents' : '') + ', or call <a href="tel:+18449008804">' + PHONE + '</a>.', true);
        });
    }, true);
  }

  /* ---------- init ---------- */
  function confirmClassicSend() {
    if (!/[?&]sent=1/.test(location.search)) return;
    var t = document.createElement('div');
    t.className = 'cpp-toast'; t.setAttribute('role', 'status');
    t.innerHTML = '<strong>Thanks, your message was sent.</strong> Our sales team will get back to you soon.';
    document.body.appendChild(t);
    setTimeout(function () { t.classList.add('is-out'); }, 7000);
    if (history.replaceState) history.replaceState(null, '', location.pathname + location.hash);
  }

  var started = false;
  function init() {
    enhanceAllSearch(); enhanceFields();
    if (started) return;  // WP Rocket re-fires DOMContentLoaded; set these up once
    started = true;
    [initQuote, initQuoteButton, initSpecPrint, initToTop, initArticle, initProductBar, initStickyBar, initHome, initFilterNav, initFluentForms, confirmClassicSend].forEach(function (f) { try { f(); } catch (err) { if (window.console) console.warn('cpp', err); } });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  // Elementor renders some widgets late; pick up search forms that appear afterwards.
  window.addEventListener('load', function () {
    setTimeout(function () { enhanceAllSearch(); loadCarouselImages(); }, 400);
    setTimeout(loadCarouselImages, 1800);  // carousels add their slide copies after start-up
  });
})();
