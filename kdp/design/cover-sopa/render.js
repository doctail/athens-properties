// Usage: node render.js <pages>   (default 119)
// Full wrap KDP, trim 8.5x11, bleed 0.125, white paper: spine = pages x 0.002252 in.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const path = require('path');

const PAGES = parseInt(process.argv[2] || '119', 10);
if (!(PAGES > 0)) { console.error('Usage: node render.js <pages>'); process.exit(1); }

const BLEED = 0.125, TRIM_W = 8.5, TRIM_H = 11, SAFE = 0.125;
const SPINE = +(PAGES * 0.002252).toFixed(4);
const W = +(BLEED + TRIM_W + SPINE + TRIM_W + BLEED).toFixed(4);
const H = TRIM_H + 2 * BLEED;
const SPINE_X = BLEED + TRIM_W;           // spine left edge
const FRONT_X = SPINE_X + SPINE;          // front trim left edge
// Spine text: 0.0625 in clearance each side (KDP), font size = clear width, clamped 9..14 pt.
const SPINE_CLEAR = 0.0625;
let spinePt = Math.floor((SPINE - 2 * SPINE_CLEAR) * 72 * 2) / 2; // half-point steps
let spineWarn = null;
if (spinePt > 14) spinePt = 14;
if (spinePt < 9) { spineWarn = `spine too narrow for 9 pt text (${spinePt} pt fits): spine text hidden`; }
if (PAGES < 79) spineWarn = (spineWarn ? spineWarn + '; ' : '') + 'KDP allows spine text only from 79 pages';

const dir = __dirname;
const htmlFile = path.join(dir, 'cover-fullwrap-es.html');
const DPI = 96;

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const prepare = async (page) => {
    await page.goto('file://' + htmlFile, { waitUntil: 'load' });
    await page.evaluate(({ W, H, SPINE, spinePt, hide }) => {
      document.getElementById('page-size').textContent = `@page { size: ${W}in ${H}in; margin: 0; }`;
      const r = document.documentElement.style;
      r.setProperty('--spine', SPINE + 'in');
      r.setProperty('--spine-font', spinePt + 'pt');
      if (hide) document.querySelector('.spine-text').style.display = 'none';
    }, { W, H, SPINE, spinePt, hide: spinePt < 9 || PAGES < 79 });
    await page.evaluate(() => document.fonts.ready);
  };
  const vp = { width: Math.ceil(W * DPI), height: Math.ceil(H * DPI) };
  const page = await browser.newPage({ viewport: vp });
  await prepare(page);

  // ---- Checks: every text run and the barcode box must sit in its panel's safe zone ----
  const report = await page.evaluate(({ BLEED, TRIM_W, TRIM_H, SAFE, SPINE_X, SPINE, FRONT_X, SPINE_CLEAR }) => {
    const px = 96, out = [];
    const zones = {
      back:  { x0: BLEED + SAFE, x1: BLEED + TRIM_W - SAFE },
      spine: { x0: SPINE_X + SPINE_CLEAR, x1: SPINE_X + SPINE - SPINE_CLEAR },
      front: { x0: FRONT_X + SAFE, x1: FRONT_X + TRIM_W - SAFE },
    };
    const y0 = BLEED + SAFE, y1 = BLEED + TRIM_H - SAFE;
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const items = [];
    let n;
    while ((n = walker.nextNode())) {
      if (!n.textContent.trim() || n.parentElement.closest('script,style')) continue;
      const host = n.parentElement;
      if (getComputedStyle(host.closest('.spine-text') || host).display === 'none') continue;
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) items.push({ el: host, r, label: n.textContent.trim().slice(0, 40), panel: host.closest('section').id });
    }
    document.querySelectorAll('[data-check]').forEach(el => items.push({ el, r: el.getBoundingClientRect(), label: el.dataset.check, panel: el.closest('section').id }));
    for (const it of items) {
      if (it.el.closest('.grid-card')) continue; // decorative grid may run into the bleed
      const z = zones[it.panel];
      const b = { x0: it.r.left / px, x1: it.r.right / px, y0: it.r.top / px, y1: it.r.bottom / px };
      if (it.panel === 'spine') { // vertical text: compare the em box (glyph height incl. descenders) with the spine
        const em = parseFloat(getComputedStyle(it.el).fontSize) / px, cx = (b.x0 + b.x1) / 2;
        b.x0 = cx - em / 2; b.x1 = cx + em / 2;
      }
      const ok = b.x0 >= z.x0 - 1e-3 && b.x1 <= z.x1 + 1e-3 && b.y0 >= y0 - 1e-3 && b.y1 <= y1 + 1e-3;
      if (!ok) out.push(`${it.panel}: "${it.label}" box x ${b.x0.toFixed(3)}-${b.x1.toFixed(3)} y ${b.y0.toFixed(3)}-${b.y1.toFixed(3)} outside safe x ${z.x0.toFixed(3)}-${z.x1.toFixed(3)} y ${y0}-${y1}`);
    }
    return { violations: out, checked: items.length };
  }, { BLEED, TRIM_W, TRIM_H, SAFE, SPINE_X, SPINE, FRONT_X, SPINE_CLEAR });

  // Contrast of the colour pairs used
  const lum = h => { const c = [1, 3, 5].map(i => parseInt(h.substr(i, 2), 16) / 255).map(v => v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; };
  const cr = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return ((x + 0.05) / (y + 0.05)).toFixed(2); };

  // Chromium quantises the PDF page width (about 1/75 in), so render slightly wider and crop the
  // MediaBox to the exact KDP size with pypdf (content is anchored top-left; extra is right-edge bleed colour).
  const pdfPath = path.join(dir, 'cover-fullwrap-es.pdf');
  await page.pdf({ path: pdfPath, width: (W + 0.03) + 'in', height: H + 'in', printBackground: true, pageRanges: '1' });
  const py = `import sys, pypdf
r = pypdf.PdfReader(sys.argv[1]); w = pypdf.PdfWriter()
pg = r.pages[0]; W, H = float(sys.argv[2]), float(sys.argv[3])
top = float(pg.mediabox.top)
box = pypdf.generic.RectangleObject([0, top - H, W, top])
pg.mediabox = box; pg.cropbox = box; pg.trimbox = box; pg.bleedbox = box
w.add_page(pg); w.write(sys.argv[1])
print('pdf %.3f x %.3f pt = %.4f x %.4f in' % (W, H, W / 72, H / 72))`;
  console.log(execFileSync('python3', ['-c', py, pdfPath, String(W * 72), String(H * 72)]).toString().trim());
  await page.screenshot({ path: path.join(dir, 'preview-full.png'), fullPage: false });
  // Front trim at 3x for the thumbnail, then downscale with Lanczos to 150 px width
  const hi = path.join(dir, '.front-hi.png');
  const p2 = await browser.newPage({ viewport: vp, deviceScaleFactor: 3 });
  await prepare(p2);
  await p2.screenshot({ path: hi, clip: { x: FRONT_X * DPI, y: BLEED * DPI, width: TRIM_W * DPI, height: TRIM_H * DPI } });
  await browser.close();
  execFileSync('convert', [hi, '-filter', 'Lanczos', '-resize', '150x', path.join(dir, 'thumb-front-150.png')]);

  console.log(`pages ${PAGES} | spine ${SPINE} in | total ${W} x ${H} in | spine x ${SPINE_X}-${(SPINE_X + SPINE).toFixed(4)} | front trim x ${FRONT_X.toFixed(4)}-${(FRONT_X + TRIM_W).toFixed(4)}`);
  console.log(`spine text ${spinePt} pt${spineWarn ? ' | WARNING: ' + spineWarn : ''}`);
  console.log(`contrast white/#1E4D3A ${cr('#FFFFFF', '#1E4D3A')}:1 | #1A1A1A/white ${cr('#1A1A1A', '#FFFFFF')}:1 | white/#1A1A1A spine ${cr('#FFFFFF', '#1A1A1A')}:1`);
  console.log(`safe-zone: ${report.checked} boxes checked, ${report.violations.length} violations`);
  report.violations.forEach(v => console.log('  ' + v));
})().catch(e => { console.error(e); process.exit(1); });
