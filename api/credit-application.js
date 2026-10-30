// Credit application sender: emails the applicant's PDF (built in the browser) plus their
// tax permit to the sales inbox through Resend (https://resend.com).
//
// Vercel environment variables:
//   RESEND_API_KEY  required - from resend.com > API Keys
//   MAIL_TO         optional - comma-separated recipients (default: adir@arunlimitedsupply.com)
//   MAIL_FROM       optional - verified sender, e.g. "Crown Website <applications@crownplasticandpaper.com>"
//                   (default: Resend's shared sender, which can only deliver to the Resend account owner)

const MAX_BODY = 4_300_000;           // Vercel caps request bodies at 4.5 MB
const MAX_FILES = 4;
const ALLOWED_TYPES = /^(application\/pdf|image\/(jpeg|png|webp|heic|heif))$/;

function clean(v, n = 300) {
  return String(v == null ? '' : v).replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, n);
}
function esc(v) {
  return clean(v, 2000).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
function safeName(v, fallback) {
  const n = clean(v, 120).replace(/[^\w .()&-]+/g, '').replace(/\s+/g, ' ').trim();
  return n || fallback;
}

module.exports = async function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ ok: false, error: 'method' });

  const key = process.env.RESEND_API_KEY;
  if (!key) return res.status(503).json({ ok: false, error: 'not_configured' });

  const len = Number(req.headers['content-length'] || 0);
  if (len > MAX_BODY) return res.status(413).json({ ok: false, error: 'too_large' });

  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = null; } }
  if (!body || typeof body !== 'object') return res.status(400).json({ ok: false, error: 'bad_request' });
  if (body.website) return res.status(200).json({ ok: true });   // honeypot: quietly accept bots

  const company = clean(body.company, 150);
  const email = clean(body.email, 200);
  const pdf = typeof body.pdf === 'string' ? body.pdf : '';
  if (!company || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !pdf) {
    return res.status(400).json({ ok: false, error: 'missing_fields' });
  }

  const attachments = [{ filename: `Credit Application - ${safeName(company, 'Applicant')}.pdf`, content: pdf }];
  const files = Array.isArray(body.files) ? body.files.slice(0, MAX_FILES) : [];
  for (const f of files) {
    if (!f || typeof f.data !== 'string' || !ALLOWED_TYPES.test(String(f.type || ''))) continue;
    attachments.push({ filename: safeName(f.name, 'tax-permit'), content: f.data });
  }

  const summary = Array.isArray(body.summary) ? body.summary.slice(0, 12) : [];
  const rows = summary
    .filter((r) => r && r.value)
    .map((r) => `<tr><td style="padding:6px 12px 6px 0;color:#566275;white-space:nowrap">${esc(r.label)}</td><td style="padding:6px 0;color:#011425;font-weight:600">${esc(r.value)}</td></tr>`)
    .join('');
  const permitNote = attachments.length > 1
    ? `Tax permit attached (${attachments.length - 1} file${attachments.length > 2 ? 's' : ''}).`
    : 'No tax permit was attached - ask the applicant to send it.';
  const html = `<!doctype html><html><body style="margin:0;padding:24px;background:#F3F1EC;font-family:Helvetica,Arial,sans-serif">
<table role="presentation" width="100%" style="max-width:600px;margin:0 auto;background:#fff;border:1px solid #E3E1DB">
<tr><td style="background:#011425;padding:20px 24px;color:#fff">
<div style="font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#F2B544">New credit application</div>
<div style="font-size:22px;font-weight:700;margin-top:4px">${esc(company)}</div></td></tr>
<tr><td style="padding:20px 24px;font-size:14px;line-height:1.5;color:#011425">
<p style="margin:0 0 14px">The full application is attached as a PDF. ${esc(permitNote)}</p>
<table role="presentation" style="font-size:14px;border-collapse:collapse">${rows}</table>
<p style="margin:18px 0 0;color:#566275;font-size:12px">Reply to this email to answer the applicant directly. Sent from crownplasticandpaper.com.</p>
</td></tr></table></body></html>`;

  const to = (process.env.MAIL_TO || 'adir@arunlimitedsupply.com').split(',').map((s) => s.trim()).filter(Boolean);
  const from = process.env.MAIL_FROM || 'Crown Website <onboarding@resend.dev>';

  try {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from, to, reply_to: email,
        subject: `Credit application - ${company}`,
        html, attachments,
      }),
    });
    const out = await r.json().catch(() => ({}));
    if (!r.ok) {
      console.error('resend error', r.status, out && out.message);
      return res.status(502).json({ ok: false, error: 'send_failed' });
    }
    return res.status(200).json({ ok: true, id: out.id || null });
  } catch (err) {
    console.error('resend request failed', err && err.message);
    return res.status(502).json({ ok: false, error: 'send_failed' });
  }
};
