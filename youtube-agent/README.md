# YouTube Video Creator Agent

OpenRouter AI creates the script, audio direction, video storyboard,
and thumbnail brief. Free renderers turn those into files. You run it;
Ember creates the script.

## Who does what

- **Ember creates the script.** Run `--stage script` and it writes
  `script.json` as DRAFT using a free OpenRouter LLM.
- **You run the rest.** Read `script.json`, fix it if needed, then run
  with `--approve --upload` and it makes audio, video, thumbnail,
  and uploads the video to YouTube as unlisted.

## Setup

```bash
pip install -r requirements.txt
# ffmpeg installed on your machine
# edge-tts installed for audio: pip install edge-tts
export OPENROUTER_API_KEY=sk-or-...   # free key: https://openrouter.ai/keys
```

One-time YouTube setup, only for upload:
1. Google Cloud project, enable YouTube Data API v3.
2. Create an OAuth client ID (Desktop app), download it as
   `client_secrets.json` in the folder you run from.
3. First upload opens a browser for you to authorise. The token is
   cached in `token.pickle` afterwards.

Never commit `OPENROUTER_API_KEY`, `client_secrets.json`, or `token.pickle`.
They are in `.gitignore`.

## Run

```bash
# 1. Ember's job: create the script (DRAFT, stops at the human gate)
python3 agent.py --topic "LoRA" --mode long --facts "LoRA: 10000x fewer trainable params, 3x less GPU memory, arXiv 2106.09685" --out lora-episode

# 2. Read lora-episode/script.json, approve it, then run the whole thing
python3 agent.py --topic "LoRA" --mode long --out lora-episode --stage all --approve --upload

# 3. Dry run, no key needed, writes templates only
python3 agent.py --topic "LoRA" --mode long --stage all --dry-run --approve --upload --out /tmp/test-video
```

## Smart rendering: many shorts, merged into one long video

A 10-minute render fails as a whole. A 60-second segment fails alone.
So the script is split into segments of at most 150 words (~70 seconds
each). Each segment is rendered on its own — own audio, own title card,
own captions — then all segments are merged with ffmpeg concat into
`video.mp4`. A failed segment is re-rendered alone:

```bash
python3 agent.py --topic "LoRA" --out lora-episode --stage audio --approve --segment segment-03
python3 agent.py --topic "LoRA" --out lora-episode --stage video --approve --segment segment-03
```

Each segment is also a ready Short on its own: same audio, vertical
1080x1920 card. So one run gives you the long video *and* the Shorts.

## What each stage does

| Stage | OpenRouter AI does | Renderer does |
|---|---|---|
| script | Writes narration JSON | — |
| audio | Voice direction: pace, pauses, stress, pronunciation | Edge TTS speaks it, one .mp3 per segment |
| video | Storyboard: one scene per segment | ffmpeg renders each segment, then merges them |
| thumbnail | 3 options + image prompt | Pollinations renders thumbnail.jpg |
| upload | — | YouTube Data API, unlisted by default |

OpenRouter is a text LLM. It cannot speak, render video, or draw.
It writes the words and plans; the free tools above turn them into
audio, video, and an image.

## Files per video

`script.json`, `script_prompt.txt`, `storyboard.json`, `video_plan.json`,
`thumbnail.json`, `thumbnail.jpg`, `audio/narration.txt`,
`audio/voice_direction.json`, `audio/voice.mp3`, `video.mp4`,
`run_report.json`.
