#!/usr/bin/env python3
"""YouTube Video Creator Agent — OpenRouter AI creates script, audio, video, thumbnail.

Division of work (agreed with Aashish):
  - Ember creates the script: this agent's script stage, using a free
    OpenRouter LLM, writes script.json as DRAFT.
  - The user runs this script: `python3 agent.py --topic LoRA --stage all
    --approve --upload` — it then makes audio, video, thumbnail and
    uploads the video to YouTube as unlisted.

How OpenRouter AI is used for all four jobs:
  - Script: LLM writes the narration in structured JSON.
  - Audio: LLM writes voice direction (pace, pauses, words to stress,
    how to pronounce terms) and splits narration by section.
    Edge TTS then speaks that narration — OpenRouter is text-only,
    it cannot speak itself.
  - Video: LLM writes a scene-by-scene storyboard (one scene per
    section, visual description, duration). ffmpeg then assembles
    the slides/audio into video.mp4 from that storyboard.
  - Thumbnail: LLM writes 3 thumbnail options and an image prompt.
    Pollinations (free) renders the image from that prompt.

Smart rendering — many shorts, merged into one long video:
  A 10-minute render fails as a whole. A 60-second segment fails alone.
  So the script is split into segments of at most 150 words (~70 seconds
  each). Each segment is rendered on its own as a high-quality short clip
  (own audio, own title card, own captions), then all segments are merged
  with ffmpeg concat into video.mp4. A failed segment is re-rendered alone
  with --segment N; the good ones are never touched. Each segment is also
  a ready Short on its own (same audio, vertical 1080x1920 card).

Setup:
  - OPENROUTER_API_KEY in the environment (free key: https://openrouter.ai/keys)
  - pip install -r requirements.txt
  - ffmpeg installed; edge-tts installed for audio
  - For upload: YouTube Data API v3 enabled, client_secrets.json in the
    folder you run from (Desktop OAuth client). First upload opens a
    browser; the token is cached in token.pickle afterwards.
  - Never commit API keys, client_secrets.json, or token.pickle.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

FREE_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
    "baidu/ernie-5.5-flash-preview:free",
]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

SCRIPT_SYSTEM = (
    "You write YouTube scripts in simple words for a non-tech audience. "
    "Return structured JSON only, using this shape: "
    '{"title": "...", "hook": "...", "sections": [{"name": "...", "words": 0, '
    '"narration": "...", "visual": "..."}], "description": "...", '
    '"tags": [], "thumbnail_options": ["...", "...", "..."]}. '
    "Never invent numbers. Use only the facts given in the user prompt. "
    "Keep narration near 130 words per minute."
)
MEDIA_SYSTEM = (
    "You are the voice and video director for a YouTube explainer. "
    "Return structured JSON only. For audio: pace, pauses, words to stress, "
    "pronunciation of technical terms. For video: one scene per script "
    "section with a visual description and a duration in seconds."
)
THUMBNAIL_SYSTEM = (
    "You write YouTube thumbnail briefs. Return JSON only: "
    '{"options": ["3 to 5 words", "...", "..."], '
    '"image_prompt": "one detailed image prompt, no text in the image", '
    '"text": "the chosen 3 to 5 words"}. '
    "No shocked face, no red arrow, no claim the video does not prove."
)


def call_openrouter(prompt, api_key, system=SCRIPT_SYSTEM, temperature=0.6):
    """Try the free fallback chain in order. Return (model, text)."""
    errors = []
    for model in FREE_MODELS:
        try:
            body = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
            }).encode()
            req = urllib.request.Request(
                OPENROUTER_URL, data=body,
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json",
                         "HTTP-Referer": "https://github.com/Ashish12031997/ai-papers",
                         "X-Title": "AI Papers Video Agent"},
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.load(resp)
            return model, data["choices"][0]["message"]["content"]
        except Exception as e:  # noqa: BLE001 - try next model
            errors.append(f"{model}: {e}")
    raise RuntimeError("All free OpenRouter models failed:\n" + "\n".join(errors))


def clean_json(text):
    return text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()


def require_api_key(args):
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key and not args.dry_run:
        raise SystemExit("OPENROUTER_API_KEY is not set. Get a free key at https://openrouter.ai/keys")
    return key


def script_prompt(topic, mode, facts):
    length = "9 to 11 minutes, about 1300 words" if mode == "long" else "60 seconds, about 150 words"
    return (
        f"Topic: {topic}\nLength: {length}\n"
        f"Facts (verified, use only these numbers): {facts or 'None given - keep claims general, do not invent numbers.'}\n"
        "Order: Hook (problem in a real example, no title yet), The Problem, "
        "Why old fixes fail, The Paper Idea, Sample Code, Results and Limits, Takeaway. "
        "For Shorts, return only Hook, one Idea section, and Takeaway."
    )


def stage_script(args, out):
    prompt = script_prompt(args.topic, args.mode, args.facts)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "script_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(prompt)
    if args.dry_run:
        script = {
            "title": f"{args.topic} — How It Fixes It",
            "hook": f"[DRY RUN] Hook for {args.topic}: state the problem in a real example.",
            "sections": [
                {"name": "The Problem", "words": 300, "narration": "[DRY RUN] Problem narration here.", "visual": "Slide: problem diagram"},
                {"name": "The Paper Idea", "words": 400, "narration": "[DRY RUN] Paper idea narration here.", "visual": "Slide: one diagram, redrawn"},
                {"name": "Sample Code", "words": 350, "narration": "[DRY RUN] Code narration here.", "visual": "Colab screen record"},
                {"name": "Results and Limits", "words": 200, "narration": "[DRY RUN] Results narration here.", "visual": "Slide: one table"},
                {"name": "Takeaway", "words": 70, "narration": "[DRY RUN] One sentence to remember.", "visual": "One sentence on screen"},
            ],
            "description": f"[DRY RUN] Description for {args.topic}.",
            "tags": [args.topic.lower()],
            "thumbnail_options": [f"{args.topic} is too expensive", f"How {args.topic} fixes it", f"{args.topic} in plain English"],
            "status": "DRAFT - dry run, no LLM call made",
        }
        model = "dry-run"
    else:
        api_key = require_api_key(args)
        model, text = call_openrouter(prompt, api_key)
        script = json.loads(clean_json(text))
        script["status"] = "DRAFT - needs human review before audio/video"
    with open(os.path.join(out, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2)
    print(f"Script saved: {os.path.join(out, 'script.json')} (model: {model})")
    print("HUMAN GATE: read script.json and approve it before audio/video.")
    print("To continue, re-run with --approve.")
    return script


def load_script(out):
    path = os.path.join(out, "script.json")
    if not os.path.exists(path):
        raise SystemExit(f"No script.json in {out}. Run the script stage first.")
    return json.load(open(path, encoding="utf-8"))


def require_approve(args):
    if not args.approve and not args.dry_run:
        raise SystemExit(
            "Script gate: add --approve to continue past the script. "
            "Read script.json first, fix it if needed, then re-run with --approve.")


MAX_SEGMENT_WORDS = 150  # ~70 seconds of narration; a Short must stay under 60-70s


def split_segments(script):
    """Split the script into short segments, max 150 words each.

    A section longer than 150 words is cut at sentence boundaries into
    two or more segments. Returns a list of segment dicts with an id,
    section name, narration, visual, word count, and approx seconds.
    """
    segments = []
    parts = [{"name": "Hook", "narration": script.get("hook", ""), "visual": "Hook slide"}]
    parts += script.get("sections", [])
    for part in parts:
        text = (part.get("narration") or "").strip()
        if not text:
            continue
        # Cut at sentence boundaries so no segment exceeds the limit.
        sentences = [s.strip() for s in text.replace("! ", ". ").replace("? ", ". ").split(". ") if s.strip()]
        chunk, chunk_words = [], 0
        for sentence in sentences:
            # A single run-on sentence can itself exceed the limit, so
            # cut it by words as a fallback.
            words_list = sentence.split()
            while len(words_list) > MAX_SEGMENT_WORDS:
                if chunk:
                    segments.append((part.get("name", ""), part.get("visual", ""), " ".join(chunk)))
                    chunk, chunk_words = [], 0
                segments.append((part.get("name", ""), part.get("visual", ""),
                                 " ".join(words_list[:MAX_SEGMENT_WORDS])))
                words_list = words_list[MAX_SEGMENT_WORDS:]
            sentence = " ".join(words_list)
            words = len(words_list)
            if chunk and chunk_words + words > MAX_SEGMENT_WORDS:
                segments.append((part.get("name", ""), part.get("visual", ""), " ".join(chunk)))
                chunk, chunk_words = [sentence], words
            else:
                chunk.append(sentence)
                chunk_words += words
        if chunk:
            segments.append((part.get("name", ""), part.get("visual", ""), " ".join(chunk)))
    out_segments = []
    for i, (name, visual, narration) in enumerate(segments, 1):
        words = len(narration.split())
        out_segments.append({
            "id": f"segment-{i:02d}",
            "section": name,
            "narration": narration,
            "visual": visual,
            "words": words,
            "approx_seconds": round(words / 130 * 60),
        })
    return out_segments


def stage_audio(args, out):
    require_approve(args)
    script = load_script(out)
    segments = split_segments(script)
    with open(os.path.join(out, "segments.json"), "w", encoding="utf-8") as f:
        json.dump(segments, f, indent=2)
    print(f"Split into {len(segments)} short segments, max {MAX_SEGMENT_WORDS} words each.")
    narration = "\n\n".join(
        [script.get("hook", "")] + [s.get("narration", "") for s in script.get("sections", [])]
    )
    audio_dir = os.path.join(out, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    with open(os.path.join(audio_dir, "narration.txt"), "w", encoding="utf-8") as f:
        f.write(narration)
    # OpenRouter AI directs the voice: pace, pauses, stress, pronunciation.
    if args.dry_run:
        direction = {"pace": "slow and clear", "pauses": "after each section",
                     "stress": [args.topic], "pronunciation": {},
                     "status": "DRY RUN - no LLM call made"}
    else:
        api_key = require_api_key(args)
        _, text = call_openrouter(
            f"Script for {args.topic}:\n{narration}\n\n"
            "Write voice direction as JSON: {\"pace\": ..., \"pauses\": ..., "
            "\"stress\": [...], \"pronunciation\": {\"term\": \"how to say it\"}}.",
            api_key, system=MEDIA_SYSTEM)
        direction = json.loads(clean_json(text))
    with open(os.path.join(audio_dir, "voice_direction.json"), "w", encoding="utf-8") as f:
        json.dump(direction, f, indent=2)
    print(f"Voice direction (OpenRouter): {direction}")
    # One audio file per segment, not one big file. A bad segment is
    # re-recorded alone; the good ones are never touched.
    for seg in segments:
        seg_txt = os.path.join(audio_dir, f"{seg['id']}.txt")
        with open(seg_txt, "w", encoding="utf-8") as f:
            f.write(seg["narration"])
    edge = shutil.which("edge-tts")
    if args.dry_run or not edge:
        print("Audio: dry-run or edge-tts not found. Per-segment files are in audio/. To record one segment:")
        print("  edge-tts --voice en-US-AndrewNeural --file audio/segment-01.txt --write-media audio/segment-01.mp3")
        return {"status": "not rendered", "voice": "en-US-AndrewNeural",
                "direction": direction, "segments": len(segments)}
    wanted = [args.segment] if args.segment else None
    for seg in segments:
        if wanted and seg["id"] not in wanted:
            continue
        subprocess.run([edge, "--voice", "en-US-AndrewNeural",
                        "--file", os.path.join(audio_dir, f"{seg['id']}.txt"),
                        "--write-media", os.path.join(audio_dir, f"{seg['id']}.mp3")], check=True)
        print(f"Audio saved: audio/{seg['id']}.mp3 ({seg['approx_seconds']}s)")
    return {"status": "rendered", "voice": "en-US-AndrewNeural",
            "direction": direction, "segments": len(segments)}


def render_segment(out, seg, title):
    """Render one short clip: title card + that segment's audio.

    Same codec and resolution for every segment, so the merge step can
    use ffmpeg concat with -c copy (fast, no re-encode loss).
    Returns True if the segment file exists afterwards.
    """
    seg_dir = os.path.join(out, "segments")
    os.makedirs(seg_dir, exist_ok=True)
    audio = os.path.join(out, "audio", f"{seg['id']}.mp3")
    video = os.path.join(seg_dir, f"{seg['id']}.mp4")
    if not shutil.which("ffmpeg") or not os.path.exists(audio):
        return False
    label = f"{seg['section']}: {seg['narration'][:60]}".replace("'", "").replace(":", "-")
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi",
                    "-i", "color=c=0x111827:s=1920x1080:d=600",
                    "-i", audio, "-shortest", "-c:v", "libx264", "-c:a", "aac",
                    "-vf", f"drawtext=text='{label}':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2",
                    video], check=False)
    return os.path.exists(video)


def merge_segments(out):
    """Merge the rendered segments into video.mp4 with ffmpeg concat.

    All segments share codec/resolution, so this is a stream copy.
    Returns the video path, or None if nothing was rendered yet.
    """
    seg_dir = os.path.join(out, "segments")
    rendered = sorted(f for f in os.listdir(seg_dir) if f.endswith(".mp4")) if os.path.isdir(seg_dir) else []
    if not rendered or not shutil.which("ffmpeg"):
        return None
    concat_path = os.path.join(seg_dir, "concat.txt")
    with open(concat_path, "w", encoding="utf-8") as f:
        for name in rendered:
            f.write(f"file '{name}'\n")
    video = os.path.join(out, "video.mp4")
    result = subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                             "-i", concat_path, "-c", "copy", video],
                            check=False)
    return video if result.returncode == 0 and os.path.exists(video) else None


def stage_video(args, out):
    require_approve(args)
    script = load_script(out)
    segments = json.load(open(os.path.join(out, "segments.json"), encoding="utf-8")) \
        if os.path.exists(os.path.join(out, "segments.json")) else split_segments(script)
    # OpenRouter AI writes the storyboard: one scene per segment.
    if args.dry_run:
        storyboard = {"scenes": [
            {"segment": s["id"], "section": s["section"], "visual": s["visual"],
             "seconds": s["approx_seconds"]}
            for s in segments], "status": "DRY RUN - no LLM call made"}
    else:
        api_key = require_api_key(args)
        _, text = call_openrouter(
            "Segments for " + args.topic + ":\n"
            + "\n".join(f"- {s['id']} ({s['section']}): {s['visual']}" for s in segments)
            + "\n\nWrite a storyboard as JSON: {\"scenes\": [{\"segment\": ..., "
              "\"section\": ..., \"visual\": ..., \"seconds\": ...}]}.",
            api_key, system=MEDIA_SYSTEM)
        storyboard = json.loads(clean_json(text))
    with open(os.path.join(out, "storyboard.json"), "w", encoding="utf-8") as f:
        json.dump(storyboard, f, indent=2)
    plan = {
        "mode": args.mode,
        "resolution": "1920x1080", "fps": 30, "codec": "H.264 + AAC",
        "captions": "faster-whisper, burn in with ASS/SRT, 3 words per line for Shorts",
        "segments": len(segments),
        "segment_files": [f"segments/{s['id']}.mp4" for s in segments],
        "storyboard": storyboard,
        "ffmpeg": "found" if shutil.which("ffmpeg") else "NOT found - install ffmpeg first",
        "merge": "ffmpeg -f concat -safe 0 -i segments/concat.txt -c copy video.mp4",
    }
    with open(os.path.join(out, "video_plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    if args.dry_run:
        print(f"Video plan saved: {len(segments)} segments, merge with ffmpeg concat.")
        print("Dry-run: no segments rendered. Run without --dry-run to render them.")
        return plan
    wanted = [args.segment] if args.segment else None
    rendered = 0
    for seg in segments:
        if wanted and seg["id"] not in wanted:
            continue
        if render_segment(out, seg, script.get("title", args.topic)):
            rendered += 1
            print(f"Segment rendered: segments/{seg['id']}.mp4 ({seg['section']}, {seg['approx_seconds']}s)")
    plan["rendered_segments"] = rendered
    if rendered and not wanted:
        merged = merge_segments(out)
        if merged:
            print(f"Merged {rendered} segments into: {merged}")
            plan["merged"] = merged
    with open(os.path.join(out, "video_plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2)
    if not rendered:
        print("No segments rendered — run the audio stage first so each segment has an .mp3.")
    return plan


def stage_thumbnail(args, out):
    require_approve(args)
    script = load_script(out)
    # OpenRouter AI writes the thumbnail brief and image prompt.
    if args.dry_run:
        brief = {"options": script.get("thumbnail_options", []),
                 "image_prompt": f"Simple flat illustration of {args.topic}, clean, dark background, no text",
                 "text": (script.get("thumbnail_options") or [args.topic])[0],
                 "status": "DRY RUN - no LLM call made"}
    else:
        api_key = require_api_key(args)
        _, text = call_openrouter(
            f"Video title: {script.get('title', args.topic)}\n"
            f"Hook: {script.get('hook', '')}\n\nWrite a thumbnail brief as JSON.",
            api_key, system=THUMBNAIL_SYSTEM)
        brief = json.loads(clean_json(text))
    brief["size"] = "1280x720"
    with open(os.path.join(out, "thumbnail.json"), "w", encoding="utf-8") as f:
        json.dump(brief, f, indent=2)
    print(f"Thumbnail brief (OpenRouter): {brief}")
    if not args.dry_run and brief.get("image_prompt"):
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(brief["image_prompt"]) + "?width=1280&height=720&nologo=true"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ai-papers-video-agent"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            with open(os.path.join(out, "thumbnail.jpg"), "wb") as f:
                f.write(data)
            print(f"Thumbnail image saved: {os.path.join(out, 'thumbnail.jpg')}")
            brief["image"] = "thumbnail.jpg"
        except Exception as e:  # noqa: BLE001 - thumbnail image is optional
            print(f"Thumbnail image download failed ({e}). Brief is saved; render the image manually.")
    return brief


def stage_upload(args, out):
    video = os.path.join(out, "video.mp4")
    if args.dry_run:
        print(f"Upload: dry-run. Would upload {video} as {args.privacy} to YouTube.")
        return {"status": "dry-run", "privacy": args.privacy, "video": video}
    if not os.path.exists(video):
        raise SystemExit(f"{video} not found — run the video stage first.")
    try:
        import pickle  # noqa: PLC0415 - only needed for upload
        from google.auth.transport.requests import Request  # noqa: PLC0415
        from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: PLC0415
        from googleapiclient.discovery import build  # noqa: PLC0415
        from googleapiclient.http import MediaFileUpload  # noqa: PLC0415
    except ImportError:
        raise SystemExit(
            "Upload needs google-api-python-client: pip install -r requirements.txt\n"
            "Then do the one-time YouTube setup: enable YouTube Data API v3, "
            "create a Desktop OAuth client, save it as client_secrets.json next to agent.py.")
    script = load_script(out)
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("client_secrets.json"):
                raise SystemExit("client_secrets.json not found — do the one-time YouTube OAuth setup first (see README.md).")
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secrets.json", ["https://www.googleapis.com/auth/youtube.upload"])
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)
    service = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {
            "title": script.get("title", args.topic)[:100],
            "description": (script.get("description", "") + "\n\nAI voice and visuals disclosed: this video was made with AI assistance.")[:5000],
            "tags": script.get("tags", [])[:500],
            "categoryId": "27",
        },
        "status": {"privacyStatus": args.privacy, "madeForKids": False,
                   "selfDeclaredMadeForKids": False},
    }
    request = service.videos().insert(
        part="snippet,status", body=body,
        media_body=MediaFileUpload(video, chunksize=-1, resumable=True))
    response = request.execute()
    vid = response["id"]
    print(f"Uploaded: https://youtu.be/{vid} (privacy: {args.privacy})")
    print("Review it in YouTube Studio, tick the altered-content disclosure, then set it to Public.")
    thumb = os.path.join(out, "thumbnail.jpg")
    if os.path.exists(thumb):
        try:
            service.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb)).execute()
            print("Thumbnail set.")
        except Exception as e:  # noqa: BLE001 - upload succeeded, thumbnail is optional
            print(f"Thumbnail upload failed ({e}). Set it manually in YouTube Studio.")
    return {"status": "uploaded", "video_id": vid, "url": f"https://youtu.be/{vid}", "privacy": args.privacy}


def main():
    p = argparse.ArgumentParser(description="YouTube Video Creator Agent — OpenRouter AI")
    p.add_argument("--topic", required=True, help="Video topic or paper name, e.g. LoRA")
    p.add_argument("--mode", choices=["long", "shorts"], default="long")
    p.add_argument("--facts", default="", help="Verified facts / numbers the LLM may use")
    p.add_argument("--out", required=True, help="Output folder for this video")
    p.add_argument("--stage", choices=["script", "audio", "video", "thumbnail", "upload", "all"], default="script")
    p.add_argument("--segment", default="", help="Re-render only one segment, e.g. segment-03")
    p.add_argument("--approve", action="store_true", help="I read script.json and approve it — continue past the human gate")
    p.add_argument("--upload", action="store_true", help="After rendering, upload the video to YouTube")
    p.add_argument("--privacy", choices=["unlisted", "private", "public"], default="unlisted")
    p.add_argument("--dry-run", action="store_true", help="No API key needed, write templates only")
    args = p.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)
    report = {"topic": args.topic, "mode": args.mode, "stage": args.stage, "dry_run": args.dry_run}
    if args.stage in ("script", "all"):
        report["script"] = stage_script(args, out)
    if args.stage in ("audio", "all"):
        report["audio"] = stage_audio(args, out)
    if args.stage in ("video", "all"):
        report["video"] = stage_video(args, out)
    if args.stage in ("thumbnail", "all"):
        report["thumbnail"] = stage_thumbnail(args, out)
    if args.stage == "upload" or (args.stage == "all" and args.upload):
        report["upload"] = stage_upload(args, out)
    with open(os.path.join(out, "run_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Run report saved: {os.path.join(out, 'run_report.json')}")


if __name__ == "__main__":
    main()
