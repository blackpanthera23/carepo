// Renders scene.html frame-by-frame to PNGs.
// Usage: node render.js <outDir> [fps=30] [onlyTimes=comma,separated]
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright');

(async () => {
  const outDir = process.argv[2] || 'frames';
  const fps = Number(process.argv[3] || 30);
  const only = process.argv[4] ? process.argv[4].split(',').map(Number) : null;
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.addInitScript(() => { window.__RENDER__ = true; });
  await page.goto('file://' + path.resolve(__dirname, 'scene.html'));
  await page.evaluate(() => document.fonts.ready);

  const times = only || Array.from({ length: Math.round(15 * fps) }, (_, i) => i / fps);
  for (let i = 0; i < times.length; i++) {
    const url = await page.evaluate(([t, f]) => {
      window.frame(t, 5, f);
      return document.getElementById('c').toDataURL('image/png');
    }, [times[i], fps]);
    const name = only ? `t_${times[i].toFixed(2)}.png` : `f_${String(i).padStart(4, '0')}.png`;
    fs.writeFileSync(path.join(outDir, name), Buffer.from(url.split(',')[1], 'base64'));
    if (i % 50 === 0) console.log(`frame ${i}/${times.length}`);
  }
  await browser.close();
})();
