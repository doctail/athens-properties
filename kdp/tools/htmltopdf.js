const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox'] });
  const p = await b.newPage();
  await p.goto('file://' + process.argv[2]);
  await p.pdf({ path: process.argv[3], preferCSSPageSize: true, printBackground: true });
  await b.close(); console.log('pdf ok');
})().catch(e => { console.error(e.message); process.exit(1); });
