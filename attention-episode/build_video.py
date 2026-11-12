#!/usr/bin/env python3
"""Build the Attention episode video, segment by segment.

Steps: parse script.md -> split into <=150-word segments (agent's
split_segments) -> slide per segment (Pillow) -> Muse TTS audio per
segment -> ffmpeg zoompan video per segment with burned captions ->
ffmpeg concat merge into video.mp4. Each segment is also a Short.
"""
import json
import os
import re
import subprocess
import sys
import textwrap

sys.path.insert(0, "/home/hatch/workspace/youtube-agent")
from agent import split_segments  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
SLIDES = {
    "Hook": ("The animal didn't cross the street\nbecause it was too tired.",
              "Who was tired — the animal, or the street?"),
    "The Problem": ("RNNs read one word at a time.",
                    "By word 40, the start is forgotten.\nTraining took weeks — no parallel work."),
    "Why old fixes fail": ("Attention on top of an RNN — still slow.",
                           "Convolutions — only nearby words\ncan reach each other."),
    "The Paper Idea": ("Every word gets Q, K and V.",
                       "Query x Key -> weights\nWeights x Value -> new meaning\n8 heads, 512 numbers per word."),
    "Sample Code": ("demo.py — NumPy only, no GPU.",
                    "Q, K, V -> scores -> weights -> mix\nsat pays most attention to cat: 0.44"),
    "Results and Limits": ("28.4 BLEU English to German",
                           "41.8 BLEU English to French\nBase: 12 hours on 8 GPUs\nBig: 3.5 days on 8 GPUs"),
    "Takeaway": ("Let every word look at every\nother word at once.",
                 "That is attention. And it is all you need."),
}


def parse_script():
    text = open(os.path.join(BASE, "script.md"), encoding="utf-8").read()
    parts = []
    # Sections are "## 0:00 Hook (~70 words)" etc.
    for m in re.finditer(r"## [0-9:]+ ([^\(]+)\([^\)]+\)\n\n(.*?)(?=\n## |\n---)", text, re.S):
        name = m.group(1).strip()
        body = re.sub(r"\s+", " ", m.group(2).strip())
        # Strip markdown so TTS and captions never read/show asterisks
        body = re.sub(r"\*+", "", body)
        parts.append({"name": name, "narration": body, "visual": ""})
    hook = parts[0]
    script = {"hook": hook["narration"], "sections": parts[1:]}
    return script


def make_slide(seg, path):
    from PIL import Image, ImageDraw, ImageFont

    def font(size, bold=False):
        for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
        return ImageFont.load_default()

    W, H = 1920, 1080
    img = Image.new("RGB", (W, H), (17, 24, 39))
    d = ImageDraw.Draw(img)
    title, body = SLIDES.get(seg["section"], (seg["section"], ""))
    d.text((80, 60), f"ATTENTION IS ALL YOU NEED  •  {seg['section'].upper()}  •  {seg['id'].upper()}",
           font=font(34), fill=(148, 163, 184))
    y = 180
    for line in title.split("\n"):
        d.text((80, y), line, font=font(62, True), fill=(255, 255, 255))
        y += 80
    y += 30
    for line in body.split("\n"):
        d.text((80, y), line, font=font(36), fill=(96, 165, 250))
        y += 52
    # Bottom ~260px is kept clear: that is where burned captions sit.
    # Q/K/V diagram on the Paper Idea slide
    if seg["section"] == "The Paper Idea":
        for i, label in enumerate(["Q", "K", "V"]):
            x = 80 + i * 320
            d.rectangle([x, 820, x + 240, 940], outline=(96, 165, 250), width=6)
            d.text((x + 90, 855), label, font=font(64, True), fill=(255, 255, 255))
        d.text((1080, 855), "Query  x  Key  ->  weights  x  Value", font=font(40), fill=(255, 255, 255))
    d.rectangle([80, 1010, 1840, 1016], fill=(37, 99, 235))
    img.save(path)


def srt_for(seg, duration):
    """6 short caption chunks, timed evenly across the segment, so
    captions stay in the bottom third and never cover the slide."""
    words = seg["narration"].split()
    n = len(words)
    nchunks = 6
    chunks = [" ".join(words[i * n // nchunks:(i + 1) * n // nchunks]) for i in range(nchunks)]
    out = []
    for i, chunk in enumerate(chunks):
        start = duration * i / len(chunks)
        end = duration * (i + 1) / len(chunks)
        def ts(t):
            return f"{int(t//3600):02d}:{int((t%3600)//60):02d}:{int(t%60):02d},{int((t%1)*1000):03d}"
        out.append(f"{i+1}\n{ts(start)} --> {ts(end)}\n{chunk}\n")
    return "\n".join(out)


def main():
    script = parse_script()
    segments = split_segments(script)
    print(f"Segments: {len(segments)}, total words: {sum(s['words'] for s in segments)}")
    for s in segments:
        print(f"  {s['id']} {s['section']} {s['words']}w ~{s['approx_seconds']}s")
    json.dump(segments, open(os.path.join(BASE, "segments.json"), "w"), indent=2)

    for seg in segments:
        sid = seg["id"]
        # Slide
        slide = os.path.join(BASE, "slides", f"{sid}.png")
        make_slide(seg, slide)
        # Narration + audio (Muse TTS, Helio)
        audio = os.path.join(BASE, "audio", f"{sid}.mp3")
        if not os.path.exists(audio):
            subprocess.run(["/opt/hatch/bin/tts", "speak", "--output", audio,
                            "--voice", "avocado_v2:MAI_03", "--speed", "105",
                            "--text-stdin"],
                           input=seg["narration"].encode(), check=True)
        # Duration
        probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "default=noprint_wrappers=1", audio],
                               capture_output=True, text=True, check=True)
        duration = float(probe.stdout.strip().split("=")[1])
        seg["duration"] = round(duration, 2)
        # Captions
        srt = os.path.join(BASE, "segments", f"{sid}.srt")
        open(srt, "w").write(srt_for(seg, duration))
        # Video segment
        video = os.path.join(BASE, "segments", f"{sid}.mp4")
        if not os.path.exists(video):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", slide,
                            "-i", audio,
                            "-vf", "zoompan=z='min(zoom+0.0002,1.05)':d=800:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30,"
                            f"subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=40'",
                            "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                            "-movflags", "+faststart", video], check=True)
        print(f"Rendered {sid}: {duration:.1f}s -> {video}")

    json.dump(segments, open(os.path.join(BASE, "segments.json"), "w"), indent=2)
    # Merge
    concat = os.path.join(BASE, "segments", "concat.txt")
    with open(concat, "w") as f:
        for seg in segments:
            f.write(f"file '{seg['id']}.mp4'\n")
    out = os.path.join(BASE, "video.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", concat, "-c", "copy", out], check=True)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                            "-of", "default=noprint_wrappers=1", out],
                           capture_output=True, text=True, check=True)
    print(f"Merged: {out}\n{probe.stdout}")
    print(f"Total segment duration: {sum(s.get('duration', 0) for s in segments):.1f}s")


if __name__ == "__main__":
    main()
