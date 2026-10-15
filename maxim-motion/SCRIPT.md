# Maxim — 15s Motion Promo

**Format:** 1920×1080 · 30 fps · 15.0 s · 120 BPM (1 beat = 0.5 s, every cut lands on a beat)
**Palette:** Maxim yellow `#FFD21F` · ink `#111111` · white
**Type:** Inter Display Black / Bold

## Research notes
Maxim (taxi Maxim) is a ride-hailing and delivery super-app: car rides, motorbike rides,
food delivery and courier/parcel delivery in one app. It runs in 20+ countries and,
in Malaysia, more than 70 cities.

## Script

| Time | Visual | On-screen copy | Sound |
|---|---|---|---|
| 0.0–0.5 | Black. A yellow dot pops and bursts out to flood the frame | — | pop, whoosh, first kick |
| 0.5–1.75 | Kinetic type rising letter by letter | **YOUR CITY.** / **ON DEMAND.** | text thuds, beat starts |
| 1.75–2.0 | Diagonal ink stripes wipe the frame | — | swoosh |
| 2.0–3.5 | Car drives in on a moving road, speed lines, giant outline type behind | **01 RIDE** — Cars at your tap | whoosh, impact, horn "beep-beep" |
| 3.5–5.0 | Circle wipe → motorbike zips in | **02 BIKE** — Beat the traffic | whoosh, impact, engine rev |
| 5.0–6.5 | Circle wipe → steaming food bowl drops in | **03 FOOD** — Cravings, delivered | whoosh, impact, bell ding |
| 6.5–8.0 | Circle wipe → parcel lands | **04 DELIVERY** — Send it across town | whoosh, impact, box thud |
| 8.0–9.5 | Rotating dotted globe, counter rolls up | **20+ COUNTRIES** | tick-roll, impact |
| 9.5–11.0 | Counter swaps, globe spins on | **70+ CITIES IN MALAYSIA** | tick-roll, impact |
| 11.0–12.75 | Phone rises; route draws on map; finger taps **Order**; "Driver found" card pops | **Tap. / Track. / Arrive.** | whoosh, click, notification chime |
| 12.5–13.0 | Zoom into the phone screen | — | riser |
| 13.0–15.0 | Ray burst, **maxim** wordmark springs in letter by letter | **Ride. Deliver. Anything.** / Download the app | big impact, shimmer, final chord |

## Music
Original track composed in code (`audio.py`): A-minor house groove, Am–F–C–G, 120 BPM.
Kick on every beat, claps on 2 and 4, off-beat hats, a sidechained saw bass and pad,
and a 16th-note pluck arp from the first product reveal. It drops out under the riser and
lands on a final chord when the logo appears. All SFX are synthesized too, so there are no licensing issues.

## Files
- `scene.html` — the canvas animation (`window.draw(t)` renders any moment)
- `render.js` — Playwright frame renderer (450 PNG frames)
- `audio.py` — music + SFX synthesis (NumPy) → `audio.wav`
- `build.sh` — renders frames and audio, then muxes `maxim_promo.mp4`
