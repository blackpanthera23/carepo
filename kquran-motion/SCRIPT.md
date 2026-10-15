# KQuran — 15s Motion Promo

**Format:** 1920×1080 · 30 fps · 15.0 s · 120 BPM (cuts land on the beat)
**Palette:** emerald `#0B3D2E` · gold `#D9B45A` · cream `#FBF6EA`
**Type:** Playfair Display (headlines) · Plus Jakarta Sans (UI) · Amiri (Arabic letters)
**Motif:** 8-point Islamic star `{8/2}` used as tile pattern, transitions and the logo frame

## Facts used — status
kquran.my is blocked by this environment's network policy, so nothing below was read directly
from the site. The rule for this video: only claims that appeared as direct quotes from kquran.my
in search results, or that the client confirmed.

| Claim in video | Source | Status |
|---|---|---|
| Kelas online, terus dari rumah | client (no physical classes) | ✅ confirmed by client |
| Iqra' → tajwid | quoted "Pakej A: Kelas Mengaji Iqra'" + tajwid notes | ⚠️ quote via search, not read directly |
| Cikgu: Diploma Pengajian Islam & ke atas; lulus ujian tajwid & tilawah | quoted from kquran.my | ⚠️ quote via search, not read directly |
| Kelas percubaan RM8 · 15 minit | quoted from kquran.my | ⚠️ quote via search, not read directly |
| Nota Asas Tajwid PERCUMA | quoted "Nota Ringkasan Asas Tajwid … PERCUMA" | ⚠️ quote via search, not read directly |
| kquran.my | domain found in search | ⚠️ |

**Removed because they were wrong or unverified:** physical classes / Lembah Klang (wrong: there are
no physical classes), Zoom/Meet/WhatsApp, "1,000,000" mission, and "Sabar & jelas mengajar"
(came from third-party reviews).

## Script (on-screen copy in Malay)

| Time | Visual | Copy |
|---|---|---|
| 0.0–2.0 | A gold 8-point star draws itself; the pattern ripples out | **Nak baca Al-Quran / dengan lancar?** |
| 2.0–4.0 | Iqra cards flip in right-to-left: ا ب ت ث ج ح خ د | **Dari Iqra' hingga tajwid.** |
| 4.0–6.5 | Laptop slides in, tutor/student video tiles pop | **Kelas online, / terus dari rumah.** |
| 6.5–8.5 | A gold medal springs in, a check draws itself, 2 checklist items | **Cikgu bertauliah.** |
| 8.5–11.0 | Gold wipe; "RM8" slams down; a 15-minute timer fills; bonus stamp | **Kelas percubaan RM8 · 15 minit sahaja · Nota Asas Tajwid PERCUMA** |
| 11.0–12.5 | Gold stars rise | **Mula mengaji / hari ini.** |
| 12.5–15.0 | Zoom through a star → emblem + wordmark | **KQuran · HOME LEARNING · Daftar sekarang · kquran.my** |

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
