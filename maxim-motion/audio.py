"""Original soundtrack + SFX for the Maxim promo, synthesized with NumPy.

120 BPM house groove in A minor (Am-F-C-G), every hit locked to the
animation timeline in scene.html. Writes a 15 s 44.1 kHz stereo WAV.
Usage: python3 audio.py out.wav
"""
import sys
import wave
import numpy as np

SR = 44100
DUR = 15.0
N = int(SR * DUR)
BEAT = 0.5
rng = np.random.default_rng(7)

music = np.zeros((N, 2))
sfx = np.zeros((N, 2))
drums = np.zeros((N, 2))
verb_send = np.zeros((N, 2))


# ---------------------------------------------------------------- helpers
def tt(d):
    return np.arange(int(SR * d)) / SR


def add(bus, t0, sig, gain=1.0, pan=0.0, send=0.0):
    """Mix a mono or stereo signal into a bus at time t0 (s)."""
    i0 = int(round(t0 * SR))
    if i0 >= N:
        return
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.stack([sig * l, sig * r], axis=1) * np.sqrt(2)
    i1 = min(N, i0 + len(sig))
    s = sig[: i1 - max(i0, 0)] if i0 >= 0 else sig[-i0 : i1 - i0]
    bus[max(i0, 0) : i1] += s * gain
    if send:
        verb_send[max(i0, 0) : i1] += s * gain * send


def fft_filter(sig, lo=0.0, hi=SR / 2, slope=1.0):
    """Zero-phase band filter with soft edges (Butterworth-like magnitude)."""
    n = len(sig)
    f = np.fft.rfftfreq(n, 1 / SR)
    m = np.ones_like(f)
    if hi < SR / 2:
        m *= 1 / np.sqrt(1 + (f / hi) ** (4 * slope))
    if lo > 0:
        m *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (4 * slope))
    return np.fft.irfft(np.fft.rfft(sig) * m, n)


def sweep_filter(sig, center_fn, q=1.5, block=1024):
    """Time-varying band-pass via windowed overlap-add."""
    hop = block // 2
    win = np.hanning(block)
    out = np.zeros(len(sig) + block)
    padded = np.concatenate([sig, np.zeros(block)])
    f = np.fft.rfftfreq(block, 1 / SR)
    for s in range(0, len(sig), hop):
        c = max(30.0, center_fn(s / SR))
        bw = c / q
        m = np.exp(-0.5 * ((f - c) / bw) ** 2)
        seg = padded[s : s + block] * win
        out[s : s + block] += np.fft.irfft(np.fft.rfft(seg) * m, block)
    return out[: len(sig)]


def env_ad(n, a, d, curve=1.0):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d) ** curve
    return e


def saw(freq, t, phase=0.0):
    return 2 * ((t * freq + phase) % 1.0) - 1


def note(n):
    """MIDI -> Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def noise(d):
    return rng.standard_normal(int(SR * d))


# ---------------------------------------------------------------- drums
def kick(big=False):
    t = tt(0.6 if big else 0.4)
    f = 45 + 120 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * (5 if big else 8))
    click = fft_filter(noise(0.01), 1500, 8000) * np.exp(-np.arange(int(SR * 0.01)) / SR * 400)
    body[: len(click)] += click * 0.4
    return np.tanh(body * 1.6)


def clap():
    d = 0.25
    n = noise(d)
    t = tt(d)
    e = np.zeros_like(t)
    for o in (0, 0.011, 0.022):
        e += (t >= o) * np.exp(-np.maximum(0, t - o) * 90)
    e += (t >= 0.03) * 0.5 * np.exp(-np.maximum(0, t - 0.03) * 16)
    return fft_filter(n * e, 900, 3500)


def hat(open_=False):
    d = 0.18 if open_ else 0.05
    return fft_filter(noise(d), 7000) * np.exp(-tt(d) * (18 if open_ else 70))


K_HIT, CLAP, HAT, OHAT = kick(), clap(), hat(), hat(True)
KICK_BIG = kick(True)

# ---------------------------------------------------------------- harmony
# chord tones (MIDI) per bar start; bass root
CHORDS = [
    (0.0, [57, 60, 64, 67], 45),   # Am7
    (2.0, [53, 57, 60, 64], 41),   # Fmaj7
    (4.0, [48, 52, 55, 59], 48),   # Cmaj7
    (6.0, [55, 59, 62, 65], 43),   # G7
    (8.0, [57, 60, 64, 67], 45),   # Am7
    (10.0, [53, 57, 60, 64], 41),  # Fmaj7
    (12.0, [55, 59, 62, 67], 43),  # G
    (13.0, [60, 64, 67, 71, 74], 36),  # Cmaj9 — logo
]


def chord_at(t):
    cur = CHORDS[0]
    for c in CHORDS:
        if t >= c[0]:
            cur = c
    return cur


# sidechain pump (applied to bass + pad)
kick_times = [0.5 + k * BEAT for k in range(24)] + [13.0, 14.0]
tline = np.arange(N) / SR
pump = np.ones(N)
for kt in kick_times:
    m = tline >= kt
    pump[m] *= 1 - 0.65 * np.exp(-(tline[m] - kt) * 10)

# --- drums
for kt in kick_times:
    if kt < 12.5 or kt >= 13.0:
        add(drums, kt, KICK_BIG if kt == 13.0 else K_HIT, 0.95)
for b in range(2, 25):
    t0 = b * BEAT
    if t0 >= 12.5:
        break
    if b % 2 == 1 and t0 >= 1.5:
        add(drums, t0, CLAP, 0.45, pan=0.05, send=0.35)
for k in range(1, 50):
    t0 = 0.5 + k * 0.25
    if t0 >= 12.5:
        break
    off = (k % 2 == 0)  # off-beat 8th
    if off:
        add(drums, t0, OHAT if t0 >= 2 else HAT, 0.22, pan=0.3)
    elif t0 >= 2:
        add(drums, t0, HAT, 0.10, pan=-0.3)
# snare roll into the logo
for k in range(16):
    t0 = 12.5 + k * (0.5 / 16)
    add(drums, t0, CLAP, 0.12 + 0.35 * k / 16, send=0.3)

# --- bass (8ths, octave bounce)
for k in range(48):
    t0 = 0.5 + k * 0.25
    if t0 >= 12.5:
        break
    root = chord_at(t0)[2]
    n_ = root + (12 if k % 4 == 2 else 0)
    d = 0.22
    t = tt(d)
    f = note(n_)
    s = 0.6 * saw(f, t) + 0.6 * np.sin(2 * np.pi * f * t)
    bright = fft_filter(s, 0, 1400)
    dark = fft_filter(s, 0, 260)
    e1 = np.exp(-t * 25)
    sig = (bright * e1 + dark * (1 - e1)) * env_ad(len(t), 0.004, 0.18)
    add(music, t0, sig, 0.55)
# final sub
t = tt(2.0)
add(music, 13.0, np.sin(2 * np.pi * note(36) * t) * env_ad(len(t), 0.005, 0.9), 0.6)


# --- supersaw pad
def pad(notes, d, cutoff=2200):
    t = tt(d)
    s = np.zeros((len(t), 2))
    for n_ in notes:
        for j, det in enumerate((-0.12, -0.05, 0.0, 0.06, 0.13)):
            w = saw(note(n_) * 2 ** (det / 12), t, phase=rng.random())
            pan = (j - 2) / 2.5
            s[:, 0] += w * (1 - pan) / 2
            s[:, 1] += w * (1 + pan) / 2
    for ch in range(2):
        s[:, ch] = fft_filter(s[:, ch], 120, cutoff)
    return s / (len(notes) * 5)


for i, (c0, notes, _) in enumerate(CHORDS[:-1]):
    c1 = CHORDS[i + 1][0]
    d = c1 - c0
    p_ = pad(notes, d + 0.1)
    e = np.minimum(1, tt(d + 0.1) / 0.06)[:, None]
    if c0 == 0.0:
        e = np.minimum(1, tt(d + 0.1) / 0.5)[:, None] ** 2  # swell in from the dot
    add(music, c0, p_ * e * 0.9, 1.0, send=0.25)
# final chord: big, long, bright
fin = pad(CHORDS[-1][1] + [48], 2.0, cutoff=4200)
add(music, 13.0, fin * env_ad(len(fin), 0.01, 1.6)[:, None] * 1.4, 1.0, send=0.5)

# apply pump to music bus so far (drums are added after for punch)
music *= pump[:, None] ** 0.8


# --- pluck arp (16ths) from first product reveal
def pluck(f, d=0.2):
    t = tt(d)
    s = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + saw(f * 2, t) * 0.3
    e1 = np.exp(-t * 30)
    s = fft_filter(s, 200, 5000) * e1 + fft_filter(s, 200, 1200) * (1 - e1)
    return s * env_ad(len(t), 0.002, 0.09)


PATTERN = [0, 1, 2, 3, 2, 1, 2, 3]
for k in range(200):
    t0 = 2.0 + k * 0.125
    if t0 >= 12.5:
        break
    notes = chord_at(t0)[1]
    n_ = notes[PATTERN[k % 8] % len(notes)] + 12 + (12 if (k // 8) % 2 else 0)
    sig = pluck(note(n_))
    pan = 0.45 if k % 2 else -0.45
    add(music, t0, sig, 0.16, pan=pan, send=0.3)
    add(music, t0 + 0.375, sig, 0.06, pan=-pan)  # dotted-8th echo
# sparkle arp over logo
for k, n_ in enumerate([72, 76, 79, 83, 86, 88]):
    add(music, 13.05 + k * 0.125, pluck(note(n_ + 12), 0.4), 0.13, pan=(k % 2) * 0.8 - 0.4, send=0.6)


# ---------------------------------------------------------------- SFX
def whoosh(d=0.45, f0=300, f1=3500, rev=False):
    n = noise(d)
    def cf(t):
        v = t / d
        return f0 * (f1 / f0) ** (v if not rev else 1 - v)
    s = sweep_filter(n, cf, q=1.2)
    t = tt(d)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return s * e


def impact(big=False):
    d = 1.4 if big else 0.6
    t = tt(d)
    f = 32 + 70 * np.exp(-t * 10)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (2.5 if big else 6))
    crunch = fft_filter(noise(d), 60, 900) * np.exp(-t * (9 if big else 22))
    return np.tanh((sub + crunch * 0.5) * 1.5)


def thud():
    t = tt(0.18)
    f = 60 + 100 * np.exp(-t * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 22)


def pop(f0=500, f1=1400, d=0.09):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)


def tick():
    t = tt(0.012)
    return np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 400)


def bell(f=1320, d=1.2):
    t = tt(d)
    s = np.zeros_like(t)
    for r, a, dec in ((1, 1, 2.5), (2.76, 0.5, 4), (5.4, 0.25, 7), (8.93, 0.12, 10)):
        s += a * np.sin(2 * np.pi * f * r * t) * np.exp(-t * dec)
    return s * np.minimum(1, t / 0.002) * 0.5


def horn():
    t = tt(0.12)
    s = np.sign(np.sin(2 * np.pi * 415 * t)) + np.sign(np.sin(2 * np.pi * 523 * t))
    return fft_filter(s, 200, 2400) * np.minimum(1, t / 0.005) * np.minimum(1, (0.12 - t) / 0.02) * 0.4


def rev_engine(d=0.75):
    t = tt(d)
    f = 70 + 170 * (1 - np.exp(-t * 4)) + 8 * np.sin(2 * np.pi * 7 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = saw(1, ph / (2 * np.pi)) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t))
    s = fft_filter(s, 60, 1800)
    return s * np.minimum(1, t / 0.05) * np.exp(-np.maximum(0, t - 0.45) * 8)


def cardboard():
    t = tt(0.3)
    body = np.concatenate([thud(), np.zeros(len(t) - len(thud()))])
    return body + fft_filter(noise(0.3), 250, 1200) * np.exp(-t * 30) * 0.6


def chime():
    a = bell(988, 0.8) * 0.7
    b = bell(1480, 1.0) * 0.7
    out = np.zeros(len(b) + int(0.11 * SR))
    out[: len(a)] += a
    out[int(0.11 * SR) :] += b
    return out


def riser(d=0.55):
    t = tt(d)
    n = sweep_filter(noise(d), lambda s: 400 * (12 ** (s / d)), q=2.0)
    f = 220 * (6 ** (t / d))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
    return (n + tone) * (t / d) ** 2


def crash(d=1.8):
    t = tt(d)
    return fft_filter(noise(d), 5000) * np.exp(-t * 2.4) * 0.7


# timeline (seconds) — matches scene.html
add(sfx, 0.0, pop(400, 1000, 0.12), 0.8, send=0.3)
add(sfx, 0.12, whoosh(0.4, 200, 4000), 0.5)
add(sfx, 0.5, impact(), 0.7)
add(sfx, 0.58, thud(), 0.5)
add(sfx, 1.08, thud(), 0.5)
add(sfx, 1.3, whoosh(0.3, 1500, 5000), 0.18, pan=0.5)
add(sfx, 1.68, whoosh(0.4, 300, 5000), 0.6, pan=-0.3)  # stripe wipe

# product beats
for t0 in (2.0, 3.5, 5.0, 6.5):
    add(sfx, t0 - 0.18, whoosh(0.4, 250, 3500), 0.45, pan=0.4)  # circle wipe
    add(sfx, t0, impact(), 0.55)
    add(sfx, t0 + 0.14, thud(), 0.55)
    add(sfx, t0 + 1.2, whoosh(0.32, 3500, 400), 0.4, pan=0.6)  # icon exits right
add(sfx, 2.0, whoosh(0.45, 200, 2200), 0.4, pan=-0.6)  # car drives in
add(sfx, 2.48, horn(), 0.5)
add(sfx, 2.66, horn(), 0.5)
add(sfx, 3.5, rev_engine(), 0.55, pan=-0.2)
add(sfx, 5.42, bell(1568, 1.0), 0.35, send=0.4)  # food ding
add(sfx, 6.92, cardboard(), 0.8)                  # parcel lands

# stats
add(sfx, 7.82, whoosh(0.45, 200, 3000), 0.45)
for t_start, num, t_land in ((8.15, 20, 8.85), (9.65, 70, 10.35)):
    last = 0
    for i in range(int(0.75 * SR / 100)):
        tm = t_start + i * 0.01
        v = min(1, max(0, (tm - t_start) / 0.7))
        n = round((1 - (1 - v) ** 3) * num)
        if n != last:
            add(sfx, tm, tick(), 0.22, pan=0.2)
            last = n
    add(sfx, t_land - 0.05, impact(), 0.5)
    add(sfx, t_land - 0.05, pop(800, 1800, 0.08), 0.2)
add(sfx, 9.3, whoosh(0.3, 400, 4000), 0.35)

# phone
add(sfx, 10.85, whoosh(0.45, 200, 2500), 0.55)
for t0 in (11.47, 11.97, 12.44):
    add(sfx, t0, thud(), 0.4)
add(sfx, 11.35, sweep_filter(noise(0.6), lambda s: 800 + 3000 * s / 0.6, q=6) * np.sin(np.pi * tt(0.6) / 0.6), 0.25, pan=0.3)
add(sfx, 11.99, pop(1200, 2500, 0.03) + np.concatenate([tick(), np.zeros(int(0.03 * SR) - len(tick()))]), 0.6)
add(sfx, 12.2, chime(), 0.4, send=0.4, pan=0.3)

# logo
add(sfx, 12.45, riser(), 0.7)
add(sfx, 12.62, whoosh(0.38, 300, 6000), 0.5)
add(sfx, 13.0, impact(True), 0.95, send=0.3)
add(sfx, 13.0, crash(), 0.35, send=0.4)
for k in range(5):
    add(sfx, 13.06 + k * 0.06, pop(600 + k * 120, 1400 + k * 200, 0.07), 0.25, pan=(k - 2) / 3)
add(sfx, 13.42, whoosh(0.35, 800, 6000), 0.2)   # underline swoosh
add(sfx, 14.02, pop(500, 1300, 0.1), 0.45)
add(sfx, 14.05, bell(2093, 1.0), 0.18, send=0.5)

# ---------------------------------------------------------------- reverb + master
ir_t = tt(1.6)
ir = np.stack([rng.standard_normal(len(ir_t)), rng.standard_normal(len(ir_t))], 1) * np.exp(-ir_t * 3.2)[:, None]
ir[:, 0] = fft_filter(ir[:, 0], 200, 7000)
ir[:, 1] = fft_filter(ir[:, 1], 200, 7000)
ir /= np.sqrt((ir ** 2).sum(0))
L = N + len(ir_t)
wet = np.stack([np.fft.irfft(np.fft.rfft(verb_send[:, c], L) * np.fft.rfft(ir[:, c], L), L)[:N] for c in range(2)], 1)

mix = (music + drums) * 0.55 + sfx * 0.75 + wet * 0.35
# fade the last 0.35 s
fade = np.ones(N)
fade[-int(0.35 * SR):] = np.linspace(1, 0, int(0.35 * SR)) ** 1.5
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.6) / np.tanh(1.6) * 0.92  # soft-clip "limiter"

out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out, f'{N / SR:.2f}s')
