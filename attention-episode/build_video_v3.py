#!/usr/bin/env python3
"""Attention video v3 — rebuilt with the engaging-video-retention skill.

What changed vs v2 (same narration, same audio, new visuals only):
- Every segment split into 2-3 sub-shots of ~12-18s (pattern interrupt
  every 10-20s, never 40s of one static slide).
- Background palette rotates by section; one accent colour per idea.
- NO full-word burned captions (Mayer redundancy rule). The screen
  shows headlines, keywords, numbers and diagrams; the voice carries
  the sentences. Full narration ships as a separate video.srt.
- Real visual proof: an attention heatmap drawn from demo.py's actual
  weights, a Q/K/V diagram, big-number cards for results.
- Progress bar + section label on every shot; zoom alternates in/out,
  max 1.04, never cropping text.
"""
import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
PALETTES = {
    "Hook": ((32, 12, 12), (251, 191, 36)),
    "The Problem": ((17, 24, 39), (248, 113, 113)),
    "Why old fixes fail": ((30, 20, 50), (192, 132, 252)),
    "The Paper Idea": ((6, 40, 44), (34, 211, 238)),
    "Sample Code": ((10, 40, 28), (74, 222, 128)),
    "Results and Limits": ((45, 30, 5), (251, 191, 36)),
    "Takeaway and Next": ((25, 20, 60), (129, 140, 248)),
}
# Per-segment shot content: (headline, supporting line, kind)
SHOTS = {
    "segment-01": [("The animal didn't cross\nthe street because\nit was too tired.", "Who was tired?", "headline"),
                   ("WHO was tired?", "The animal — or the street?\nYou know instantly.", "question")],
    "segment-02": [("RNNs read one word\nat a time.", "A reader with a tiny notebook.", "headline"),
                   ("Word 40.", "The first words are almost gone.\nLong sentences = forgotten start.", "bignum")],
    "segment-03": [("Two problems at once.", "It forgets. And it can't\ntrain in parallel.", "headline"),
                   ("Weeks to train.", "Word 10 waits for word 9.\nOnly big labs could afford it.", "bignum")],
    "segment-04": [("Old fixes failed.", "Attention on top of an RNN?\nStill slow underneath.", "headline"),
                   ("Convolutions?", "Nearby words only.\nFar-apart words still can't reach.", "question")],
    "segment-05": [("Every word gets\nQ, K and V.", "Query: what am I looking for?\nKey: what do I offer?\nValue: what do I say?", "headline"),
                   ("Q  x  K  ->  weights", "Match scores become attention.\nWeights x Value = new meaning.", "diagram"),
                   ("it  ->  animal", "\"it\" looks at every word —\nand picks \"animal\".", "bignum")],
    "segment-06": [("8 heads at once.", "Each head watches a different\nkind of connection.", "headline"),
                   ("8 x 64 = 512", "Eight heads, 64 numbers each.\nOne sentence, eight views at once.", "bignum"),
                   ("A meeting, not a reading.", "Everyone looks at the whole\nreport at once. Nobody forgets.", "question")],
    "segment-07": [("Parallel = fast.", "Every word does it at\nthe same time. No waiting.", "headline"),
                   ("Q  K  V", "Same numbers, three lenses.\nThat is the whole trick.", "diagram")],
    "segment-08": [("demo.py — NumPy only.", "No GPU. No API key.\nRuns in under a minute.", "headline"),
                   ("ATTENTION HEATMAP", "Real output from the demo.\nDark = ignored. Bright = watched.", "heatmap")],
    "segment-09": [("sat  ->  cat   0.44", "The word \"sat\" found the word\nit belongs to. From numbers alone.", "bignum"),
                   ("ATTENTION HEATMAP", "Read a row like a map.\n\"sat\" points at \"cat\".", "heatmap"),
                   ("A toy demo — honestly.", "Numbers are random, not learned.\nThe maths is the real maths.", "question")],
    "segment-10": [("Q, K, V -> scores\n-> weights -> mix", "That is it. That is attention.\nInside ChatGPT, Gemini, all of them.", "headline"),
                   ("The same maths.", "Learned from millions of\nsentences — same three steps.", "question")],
    "segment-11": [("28.4", "BLEU, English to German.\n+2.0 over the best before it.", "bignum"),
                   ("41.8", "BLEU, English to French.\nBest single model at the time.", "bignum"),
                   ("12 hours", "Base model, state of the art,\non 8 GPUs. Big model: 3.5 days.", "bignum")],
    "segment-12": [("The catch: attention\ncosts n-squared.", "Twice the sentence =\nfour times the work.", "headline"),
                   ("Attention alone\nis not knowledge.", "It connects words.\nKnowledge comes from the data.", "question")],
    "segment-13": [("Let every word look\nat every other word.", "That is attention.\nAnd it is all you need.", "headline"),
                   ("Next: RAG.", "The model still makes things up.\nNext paper fixes that.", "question")],
}


def font(size, bold=False):
    p = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        return ImageFont.load_default()


def heatmap_png(path):
    words = ["the", "cat", "sat", "on", "the", "mat"]
    np.random.seed(1)
    d = 8
    X = np.random.randn(6, d)
    Wq, Wk, Wv = (np.random.randn(d, d) * 0.5 for _ in range(3))
    Q, K, V = X @ Wq, X @ Wk, X @ Wv
    s = Q @ K.T / np.sqrt(d)
    w = np.exp(s - s.max(axis=1, keepdims=True))
    w /= w.sum(axis=1, keepdims=True)
    img = Image.new("RGB", (1920, 1080), (6, 40, 44))
    dr = ImageDraw.Draw(img)
    dr.text((80, 40), "ATTENTION HEATMAP  •  rows ask, columns answer", font=font(34), fill=(148, 163, 184))
    cell, x0, y0 = 130, 480, 170
    for j, wd in enumerate(words):
        dr.text((x0 + j * cell + 35, y0 - 50), wd, font=font(34, True), fill=(255, 255, 255))
    for i, wd in enumerate(words):
        dr.text((x0 - 120, y0 + i * cell + 40), wd, font=font(34, True), fill=(255, 255, 255))
        for j in range(6):
            v = float(w[i, j])
            # dark blue -> bright yellow by weight
            r = int(30 + 225 * v)
            g = int(60 + 165 * v)
            b = int(120 - 90 * v)
            dr.rectangle([x0 + j * cell + 4, y0 + i * cell + 4,
                          x0 + (j + 1) * cell - 4, y0 + (i + 1) * cell - 4],
                         fill=(r, g, b))
            dr.text((x0 + j * cell + 35, y0 + i * cell + 40), f"{v:.2f}",
                    font=font(32, True), fill=(255, 255, 255) if v > 0.4 else (200, 220, 255))
    dr.text((420, 990), "Bright = pays attention. \"sat\" row: cat = 0.44 — the brightest.", font=font(34), fill=(74, 222, 128))
    img.save(path)


def make_slide(seg, shot_idx, headline, support, kind, progress, path):
    bg, accent = PALETTES[seg["section"]]
    img = Image.new("RGB", (1920, 1080), bg)
    dr = ImageDraw.Draw(img)
    total = 13
    idx = int(seg["id"].split("-")[1])
    dr.text((80, 52), f"ATTENTION IS ALL YOU NEED  •  {seg['section'].upper()}  •  {idx}/{total}",
            font=font(32), fill=(180, 190, 205))
    # progress bar
    dr.rectangle([80, 100, 1840, 112], fill=(60, 70, 90))
    dr.rectangle([80, 100, 80 + int(1760 * progress), 112], fill=accent)
    y = 200
    # Heatmap slides carry their own title inside the image; drawing the
    # slide headline underneath would peek out from behind the paste.
    if kind != "heatmap":
        for line in headline.split("\n"):
            dr.text((80, y), line, font=font(88 if kind in ("bignum", "headline") else 72, True),
                    fill=(255, 255, 255) if kind != "bignum" else accent)
            y += 110 if kind in ("bignum", "headline") else 95
        y += 30
        for line in support.split("\n"):
            dr.text((80, y), line, font=font(40), fill=(220, 225, 235))
            y += 58
    if kind == "diagram":
        for i, label in enumerate(["Q", "K", "V"]):
            x = 80 + i * 320
            dr.rectangle([x, 780, x + 240, 920], outline=accent, width=6)
            dr.text((x + 95, 815), label, font=font(64, True), fill=(255, 255, 255))
        dr.text((1080, 830), "Query x Key -> weights x Value", font=font(40), fill=(255, 255, 255))
    if kind == "question":
        dr.ellipse([1500, 700, 1800, 1000], outline=accent, width=8)
        dr.text((1610, 815), "?", font=font(140, True), fill=accent)
    if kind == "heatmap":
        hm = Image.open(os.path.join(BASE, "slides", "heatmap.png"))
        img.paste(hm.resize((1500, 844)), (210, 180))
    img.save(path)


def duration(path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1", path],
                       capture_output=True, text=True, check=True)
    return float(p.stdout.strip().split("=")[1])


def main():
    segments = json.load(open(os.path.join(BASE, "segments.json")))
    heatmap_png(os.path.join(BASE, "slides", "heatmap.png"))
    total_dur = sum(duration(os.path.join(BASE, "audio", f"{s['id']}.mp3")) for s in segments)
    print(f"Total narration: {total_dur:.1f}s, {len(segments)} segments")
    shots_dir = os.path.join(BASE, "v3-shots")
    os.makedirs(shots_dir, exist_ok=True)
    concat_lines = []
    elapsed = 0.0
    srt_lines = []
    srt_idx = 1
    for seg in segments:
        sid = seg["id"]
        audio = os.path.join(BASE, "audio", f"{sid}.mp3")
        dur = duration(audio)
        shot_defs = SHOTS[sid]
        n = len(shot_defs)
        # SRT (separate file, not burned): one entry per segment
        def ts(t):
            return f"{int(t//3600):02d}:{int((t%3600)//60):02d}:{int(t%60):02d},{int((t%1)*1000):03d}"
        srt_lines.append(f"{srt_idx}\n{ts(elapsed)} --> {ts(elapsed+dur)}\n{seg['narration']}\n")
        srt_idx += 1
        for i, (headline, support, kind) in enumerate(shot_defs):
            start = dur * i / n
            shot_dur = dur / n
            progress = (elapsed + start) / total_dur
            slide = os.path.join(shots_dir, f"{sid}-{i+1}.png")
            make_slide(seg, i, headline, support, kind, progress, slide)
            shot = os.path.join(shots_dir, f"{sid}-{i+1}.mp4")
            # Alternate the zoom anchor (centre vs right) so consecutive
            # shots move differently; zoom always in, max 1.04, never crops.
            x_expr = "'iw/2-(iw/zoom/2)'" if i % 2 == 0 else "'iw-(iw/zoom)'"
            zp = (f"zoompan=z='min(zoom+0.0002,1.04)':d=800:x={x_expr}:y='ih/2-(ih/zoom/2)':"
                  "s=1920x1080:fps=30")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", slide,
                            "-ss", str(start), "-t", str(shot_dur), "-i", audio,
                            "-vf", zp, "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-movflags", "+faststart", shot], check=True)
            concat_lines.append(f"file '{sid}-{i+1}.mp4'")
            print(f"{sid} shot {i+1}/{n} ({kind}): {shot_dur:.1f}s")
        elapsed += dur
    open(os.path.join(BASE, "video.srt"), "w").write("\n".join(srt_lines))
    concat = os.path.join(shots_dir, "concat.txt")
    open(concat, "w").write("\n".join(concat_lines) + "\n")
    out = os.path.join(BASE, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", concat, "-c", "copy", out], check=True)
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                        "-of", "default=noprint_wrappers=1", out],
                       capture_output=True, text=True, check=True)
    print(f"V3 merged: {out}\n{p.stdout}")
    print(f"Shots: {len(concat_lines)}")


if __name__ == "__main__":
    main()
