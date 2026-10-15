# KQuran — 15s Motion Promo

**Format:** 1920×1080 · 30 fps · 15.0 s · 120 BPM (cuts land on the beat)
**Palette:** emerald `#0B3D2E` · gold `#D9B45A` · cream `#FBF6EA`
**Type:** Playfair Display (headlines) · Plus Jakarta Sans (UI) · Amiri (Arabic letters)
**Motif:** 8-point Islamic star `{8/2}` used as tile pattern, transitions and the logo frame

## Research notes (kquran.my, via search; site blocked from the render box)
KQuran Home Learning is a Malaysian Quran tutoring service: learn to read the Quran fluently
from Iqra' through tajwid. Classes run online (Zoom, Google Meet, WhatsApp video) or in person,
with a tutor coming to your home in the Klang Valley. Teachers hold a diploma in Islamic studies
or higher and pass tajwid and recitation tests. A 15-minute trial class costs RM8, and every
registration comes with free basic tajwid notes. Its mission is 1,000,000 Malaysians reading
with tajwid.

## Script (on-screen copy in Malay)

| Time | Visual | Copy | Sound |
|---|---|---|---|
| 0.0–2.0 | A gold 8-point star draws itself; the star pattern ripples out across the emerald | **Nak baca Al-Quran / dengan lancar?** | bell, shimmer sweep, soft daf hits |
| 2.0–4.0 | Iris to cream; Iqra cards flip in right-to-left: ا ب ت ث ج ح خ د | **Dari Iqra' hingga tajwid.** | 8 card flicks, whooshes |
| 4.0–6.5 | Split screen: laptop video call vs. a house with a bouncing pin, "ATAU" star badge | **Kelas Online** / **Kelas Fizikal** | whooshes, pops, ding |
| 6.5–8.5 | A gold medal springs in, a check draws itself; checklist ticks on | **Cikgu bertauliah.** | boom, shimmer, check pops |
| 8.5–11.0 | Gold wipe; "RM8" slams down with a shine sweep; a 15-minute timer fills; bonus stamp | **Kelas percubaan RM8 · 15 minit sahaja · Nota Asas Tajwid PERCUMA** | big slam, coin "ching", stamp thud |
| 11.0–12.5 | Counter rolls 0 → 1,000,000 while gold stars rise | **Misi kami: rakyat Malaysia membaca Al-Quran dengan tajwid yang betul.** | tick roll, pop, riser |
| 12.5–15.0 | Zoom through a star → emblem (open mushaf on a rehal inside a star) + wordmark | **KQuran · HOME LEARNING · Daftar sekarang · kquran.my** | boom, shimmer, final "aa" chord |

## Sound
Nasheed-style on purpose, with no melodic instruments, since this is Quran-learning content:
- a daf (frame drum) maqsum groove, claps and shaker
- hummed choir harmonies (Dm–Bb–C–Dm–Gm–A) and a sung "aa" lead built with formant synthesis
- a resolve to D major on the logo

Everything, including the SFX, is synthesized in `audio.py`, so there are no licensing issues.

## Files
- `scene.html` — canvas animation (open in a browser for a live preview)
- `render.js` — Playwright frame renderer
- `audio.py` — soundtrack + SFX
- `build.sh` — full rebuild → `kquran_promo.mp4`
- `fonts/` — Amiri, Playfair Display, Plus Jakarta Sans (SIL OFL, Google Fonts)
