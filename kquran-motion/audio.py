"""Nasheed-style soundtrack + SFX for the KQuran promo, synthesized with NumPy.

No melodic instruments: frame drum (daf) percussion, claps, and hummed
vocal harmonies built with formant synthesis, 120 BPM in D minor.
Writes a 15 s 44.1 kHz stereo WAV.  Usage: python3 audio.py out.wav
"""
import sys
import wave
import numpy as np

SR = 44100
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(11)

music = np.zeros((N, 2))
drums = np.zeros((N, 2))
sfx = np.zeros((N, 2))
send = np.zeros((N, 2))


def tt(d):
    return np.arange(int(SR * d)) / SR


def add(bus, t0, sig, gain=1.0, pan=0.0, verb=0.0):
    i0 = int(round(t0 * SR))
    if i0 >= N:
        return
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], 1) * np.sqrt(2)
    i1 = min(N, i0 + len(sig))
    s = sig[: i1 - i0] * gain
    bus[i0:i1] += s
    if verb:
        send[i0:i1] += s * verb


def bandpass(sig, lo=0.0, hi=SR / 2):
    n = len(sig)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if hi < SR / 2:
        m /= np.sqrt(1 + (f / hi) ** 4)
    if lo > 0:
        m /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** 4)
    return np.fft.irfft(np.fft.rfft(sig) * m, n)


def formant(sig, formants):
    """Shape a harmonic source with vowel formants [(freq, bw, gain), ...]."""
    n = len(sig)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.zeros_like(f)
    for fc, bw, g in formants:
        m += g / (1 + ((f - fc) / (bw / 2)) ** 2)
    return np.fft.irfft(np.fft.rfft(sig) * m, n)


def sweep(sig, center_fn, q=1.5, block=1024):
    hop = block // 2
    win = np.hanning(block)
    out = np.zeros(len(sig) + block)
    pad = np.concatenate([sig, np.zeros(block)])
    f = np.fft.rfftfreq(block, 1 / SR)
    for s in range(0, len(sig), hop):
        c = max(30.0, center_fn(s / SR))
        m = np.exp(-0.5 * ((f - c) / (c / q)) ** 2)
        out[s:s + block] += np.fft.irfft(np.fft.rfft(pad[s:s + block] * win) * m, block)
    return out[: len(sig)]


def noise(d):
    return rng.standard_normal(int(SR * d))


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ------------------------------------------------------------ percussion
def dum():
    t = tt(0.45)
    f = 62 + 70 * np.exp(-t * 30)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    skin = bandpass(noise(0.45), 80, 600) * np.exp(-t * 35) * 0.35
    jingle = bandpass(noise(0.45), 6000) * np.exp(-t * 14) * 0.12  # daf rings
    return np.tanh((body + skin + jingle) * 1.4)


def tak():
    t = tt(0.22)
    ring = np.sin(2 * np.pi * 380 * t) * np.exp(-t * 45) * 0.5
    slap = bandpass(noise(0.22), 1800, 6000) * np.exp(-t * 60)
    jingle = bandpass(noise(0.22), 7000) * np.exp(-t * 18) * 0.25
    return ring + slap + jingle


def clap():
    t = tt(0.25)
    e = sum((t >= o) * np.exp(-np.maximum(0, t - o) * 90) for o in (0, 0.012, 0.024))
    e = e + (t >= 0.03) * 0.45 * np.exp(-np.maximum(0, t - 0.03) * 15)
    return bandpass(noise(0.25) * e, 900, 3500)


def shaker():
    t = tt(0.07)
    return bandpass(noise(0.07), 5000) * np.sin(np.pi * t / 0.07) ** 2


DUM, TAK, CLAP, SHK = dum(), tak(), clap(), shaker()

# maqsum-like pattern over 8 eighths: D T . T D . T .
PAT = ['D', 'T', None, 'T', 'D', None, 'T', None]
for bar in range(1, 6):          # 2.0 .. 12.0
    b0 = bar * 2.0
    for k, h in enumerate(PAT):
        t0 = b0 + k * 0.25
        if h == 'D':
            add(drums, t0, DUM, 0.9)
        elif h == 'T':
            add(drums, t0, TAK, 0.45 if k != 6 else 0.55, pan=0.15, verb=0.15)
    for k in (1, 3):
        add(drums, b0 + k * 0.5, CLAP, 0.3, pan=-0.1, verb=0.35)
    for k in range(16):
        add(drums, b0 + k * 0.125, SHK, 0.07 + 0.05 * (k % 2), pan=0.4)
# intro: soft dums on the downbeats with the hook text
for t0 in (0.5, 1.0, 1.5):
    add(drums, t0, DUM, 0.45)
# roll into the logo
for k in range(12):
    add(drums, 12.0 + k * (0.5 / 12), TAK, 0.15 + 0.4 * k / 12, verb=0.2)
add(drums, 12.5, DUM, 1.1)
for t0, h in ((13.0, 'D'), (13.5, 'T'), (13.75, 'T'), (14.0, 'D')):
    add(drums, t0, DUM if h == 'D' else TAK, 0.55 if h == 'D' else 0.3)

# ------------------------------------------------------------ voices
AA = [(700, 130, 1.0), (1220, 150, 0.5), (2600, 220, 0.25)]
OO = [(320, 90, 1.0), (800, 110, 0.35), (2400, 200, 0.08)]
MM = [(250, 80, 1.0), (1000, 300, 0.1)]   # closed-mouth hum


def voice(midi, d, vowel=OO, vib=5.2, depth=0.008, attack=0.12, release=0.3, bright=1.0):
    t = tt(d)
    f = hz(midi) * (1 + depth * np.sin(2 * np.pi * vib * t + rng.random() * 6) * np.minimum(1, t / 0.4))
    ph = np.cumsum(f) / SR
    src = np.zeros_like(t)
    for h in range(1, 30):
        if hz(midi) * h > 9000:
            break
        src += np.sin(2 * np.pi * h * ph) / h ** (1.1 / bright)
    src += 0.02 * bandpass(noise(d), 2000, 7000)  # breath
    s = formant(src, vowel)
    env = np.minimum(1, t / attack) * np.minimum(1, np.maximum(0, d - t) / release)
    return s * env


def choir(notes, d, vowel=OO, gain=1.0):
    out = np.zeros((int(SR * d), 2))
    for i, n in enumerate(notes):
        for j, det in enumerate((-0.07, 0.07)):
            v = voice(n + det, d, vowel)
            pan = ((i + j) % 3 - 1) * 0.5
            out[:, 0] += v * (1 - pan) / 2
            out[:, 1] += v * (1 + pan) / 2
    return out / (len(notes) * 2) * gain


# D minor: Dm - Bb - C - Dm - Gm - A  (bars of 2 s), resolve to D major on the logo
CHORDS = [
    (0.0, [50, 57, 62, 65]),     # Dm
    (2.0, [46, 58, 62, 65]),     # Bb
    (4.0, [48, 55, 60, 64]),     # C
    (6.0, [50, 57, 62, 65]),     # Dm
    (8.0, [43, 55, 58, 62]),     # Gm
    (10.0, [45, 57, 61, 64]),    # A
    (12.0, [45, 57, 61, 64]),    # A (held under the riser)
]
for i, (c0, notes) in enumerate(CHORDS):
    c1 = CHORDS[i + 1][0] if i + 1 < len(CHORDS) else 12.5
    d = c1 - c0 + 0.25
    vowel = MM if c0 < 2 else OO
    g = 1.2 if c0 >= 2 else 1.0
    add(music, c0, choir(notes, d, vowel, g), 1.0, verb=0.45)

# final: open "aa" D major, swelling then fading
fin = choir([38, 50, 57, 62, 66, 69], 2.5, AA, 1.6)
fin *= (np.minimum(1, tt(2.5) / 0.05) * np.exp(-tt(2.5) * 0.9))[:, None]
add(music, 12.5, fin, 1.0, verb=0.6)

# lead hum: nasheed-like phrase in D (hijaz colour on the A chord)
MEL = [  # (start, midi, dur)
    (2.0, 69, 0.5), (2.5, 70, 0.25), (2.75, 69, 0.25), (3.0, 67, 0.5), (3.5, 65, 0.5),
    (4.0, 67, 0.75), (4.75, 65, 0.25), (5.0, 64, 0.5), (5.5, 62, 0.5),
    (6.0, 65, 0.5), (6.5, 67, 0.5), (7.0, 69, 0.75), (7.75, 70, 0.25),
    (8.0, 70, 0.5), (8.5, 69, 0.5), (9.0, 67, 0.5), (9.5, 65, 0.5),
    (10.0, 64, 0.5), (10.5, 65, 0.25), (10.75, 64, 0.25), (11.0, 61, 0.5), (11.5, 64, 0.5),
    (12.0, 69, 0.5),
]
for t0, m, d in MEL:
    v = voice(m, d + 0.12, AA, vib=5.6, depth=0.012, attack=0.04, release=0.1, bright=1.2)
    add(music, t0, v, 0.5, pan=0.05, verb=0.4)
    add(music, t0 + 0.375, v, 0.12, pan=-0.5)   # echo
for t0, m, d in ((12.6, 74, 0.4), (13.0, 78, 0.4), (13.4, 81, 1.4)):
    add(music, t0, voice(m, d, AA, vib=5.6, depth=0.014, attack=0.05, release=0.5, bright=1.2), 0.38, verb=0.6)


# ------------------------------------------------------------ SFX
def whoosh(d=0.45, f0=300, f1=3500):
    s = sweep(noise(d), lambda u: f0 * (f1 / f0) ** (u / d), q=1.2)
    return s * np.sin(np.pi * np.clip(tt(d) / d, 0, 1)) ** 2


def boom(big=False):
    d = 1.6 if big else 0.7
    t = tt(d)
    f = 34 + 60 * np.exp(-t * 9)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.2 if big else 5.5))
    air = bandpass(noise(d), 60, 1200) * np.exp(-t * (8 if big else 20)) * 0.4
    return np.tanh((sub + air) * 1.4)


def bell(f=1320, d=1.4):
    t = tt(d)
    s = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * k)
            for r, a, k in ((1, 1, 2.2), (2.76, 0.45, 3.5), (5.4, 0.2, 6), (8.93, 0.1, 9)))
    return s * np.minimum(1, t / 0.002) * 0.45


def shimmer(d=1.2, f0=2000):
    out = np.zeros(int(SR * d))
    for k in range(10):
        b = bell(f0 * 2 ** (rng.integers(0, 12) / 12), 0.8) * 0.4
        i = int(k * 0.06 * SR)
        n = min(len(b), len(out) - i)
        out[i:i + n] += b[:n] * (1 - k / 12)
    return out


def flick():
    t = tt(0.09)
    return bandpass(noise(0.09), 1500, 7000) * np.exp(-t * 55) + np.sin(2 * np.pi * 900 * t) * np.exp(-t * 90) * 0.2


def pop(f0=500, f1=1400, d=0.09):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)


def tick(f=2600):
    t = tt(0.012)
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 400)


def coin():
    a, b = bell(2637, 0.9), bell(3520, 1.0)
    o = np.zeros(len(b) + int(0.07 * SR))
    o[: len(a)] += a
    o[int(0.07 * SR):] += b
    return o


def stamp():
    t = tt(0.35)
    body = boom()[: len(t)] * 0.7
    return body + bandpass(noise(0.35), 300, 2000) * np.exp(-t * 35) * 0.6


def riser(d=0.5):
    t = tt(d)
    n = sweep(noise(d), lambda u: 400 * 14 ** (u / d), q=2.0)
    tone = np.sin(2 * np.pi * np.cumsum(220 * 6 ** (t / d)) / SR) * 0.25
    return (n + tone) * (t / d) ** 2


# 0–2 hook
add(sfx, 0.0, bell(880, 2.0), 0.35, verb=0.6)
add(sfx, 0.02, sweep(noise(0.75), lambda u: 3000 + 6000 * u / 0.75, q=3) * np.sin(np.pi * tt(0.75) / 0.75), 0.18, pan=-0.3)
add(sfx, 0.55, whoosh(0.35, 400, 3000), 0.25, pan=-0.4)
add(sfx, 1.05, whoosh(0.35, 400, 3000), 0.25, pan=0.4)
add(sfx, 1.6, whoosh(0.45, 200, 5000), 0.55)
add(sfx, 2.0, boom(), 0.5)
# 2–4 iqra cards
for i in range(8):
    add(sfx, 2.05 + i * 0.07, flick(), 0.35, pan=0.6 - i * 0.15)
add(sfx, 2.95, whoosh(0.3, 600, 4000), 0.25, pan=-0.3)
add(sfx, 3.25, whoosh(0.3, 600, 4000), 0.25, pan=0.3)
add(sfx, 3.68, whoosh(0.35, 300, 5000), 0.45)
# 4–6.5 online class
add(sfx, 3.9, whoosh(0.4, 200, 3000), 0.5, pan=-0.6)
add(sfx, 4.0, boom(), 0.45)
add(sfx, 4.25, pop(700, 1500), 0.3, pan=-0.4)
add(sfx, 4.4, pop(800, 1700), 0.3, pan=-0.3)
add(sfx, 4.3, whoosh(0.3, 600, 4000), 0.25, pan=0.4)
add(sfx, 4.6, whoosh(0.3, 600, 4000), 0.25, pan=0.4)
add(sfx, 4.5, bell(1175, 0.9), 0.22, verb=0.4)   # call connects
add(sfx, 4.62, bell(1568, 1.0), 0.22, verb=0.4)
add(sfx, 6.2, whoosh(0.35, 3000, 300), 0.45)
# 6.5–8.5 teachers
add(sfx, 6.5, boom(), 0.5)
add(sfx, 6.5, shimmer(1.0, 1800), 0.25, verb=0.5)
add(sfx, 6.85, bell(1568, 1.2), 0.3, verb=0.4)
for k in range(2):
    add(sfx, 7.05 + k * 0.28, pop(900, 2000, 0.06), 0.35, pan=0.3)
    add(sfx, 7.15 + k * 0.28, tick(3000), 0.3, pan=0.3)
# 8.5–11 RM8
add(sfx, 8.4, whoosh(0.4, 300, 5000), 0.5, pan=-0.5)
add(sfx, 8.6, whoosh(0.3, 800, 4000), 0.2)
add(sfx, 8.85, riser(0.15) * 0.5, 0.6)
add(sfx, 9.0, boom(True), 0.8, verb=0.3)
add(sfx, 9.0, coin(), 0.35, verb=0.4)
add(sfx, 9.5, pop(500, 1300, 0.1), 0.4)
add(sfx, 9.5, whoosh(0.4, 2000, 8000), 0.15)  # shine
add(sfx, 10.0, stamp(), 0.7)
add(sfx, 10.72, whoosh(0.35, 300, 4000), 0.45)
# 11–12.5 call to start
add(sfx, 10.95, boom(), 0.3)
add(sfx, 11.05, whoosh(0.35, 400, 3500), 0.3, pan=-0.3)
add(sfx, 11.4, whoosh(0.35, 400, 3500), 0.3, pan=0.3)
add(sfx, 11.4, bell(1760, 1.0), 0.18, verb=0.5)
add(sfx, 12.0, riser(0.5), 0.6)
# 12.5–15 logo
add(sfx, 12.5, boom(True), 1.0, verb=0.35)
add(sfx, 12.5, shimmer(1.6, 2200), 0.35, verb=0.6)
for k in range(6):
    add(sfx, 12.78 + k * 0.05, pop(600 + k * 100, 1400 + k * 150, 0.07), 0.2, pan=(k - 2.5) / 3)
add(sfx, 13.65, pop(500, 1300, 0.1), 0.45)
add(sfx, 14.1, whoosh(0.4, 2000, 9000), 0.15)
add(sfx, 14.1, bell(2349, 1.0), 0.15, verb=0.5)

# ------------------------------------------------------------ reverb + master
ir_t = tt(2.0)
ir = np.stack([rng.standard_normal(len(ir_t)) for _ in range(2)], 1) * np.exp(-ir_t * 2.6)[:, None]
for c in range(2):
    ir[:, c] = bandpass(ir[:, c], 200, 6500)
ir /= np.sqrt((ir ** 2).sum(0))
L = N + len(ir_t)
wet = np.stack([np.fft.irfft(np.fft.rfft(send[:, c], L) * np.fft.rfft(ir[:, c], L), L)[:N] for c in range(2)], 1)

music /= np.max(np.abs(music)) + 1e-9
drums /= np.max(np.abs(drums)) + 1e-9
sfx /= np.max(np.abs(sfx)) + 1e-9
wet /= np.max(np.abs(wet)) + 1e-9
mix = music * 0.55 + drums * 0.6 + sfx * 0.7 + wet * 0.25
fade = np.ones(N)
fade[-int(0.4 * SR):] = np.linspace(1, 0, int(0.4 * SR)) ** 1.5
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.5) / np.tanh(1.5) * 0.92

out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out, f'{N / SR:.2f}s')
