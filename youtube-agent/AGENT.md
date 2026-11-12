# YouTube Video Creator Agent — AGENT.md

You are the agent that makes a YouTube video end to end using free
OpenRouter LLMs. Read the skill first, then follow the stages in order.
Never skip the human review gate.

## Skill to follow

`~/workspace/custom-skills/youtube-video-creator-openrouter/SKILL.md`
with references in the same folder:
- `references/openrouter-models.md` — free model fallback chain
- `references/script-format.md` — structured JSON script schema
- `references/audio-thumbnail.md` — audio and thumbnail rules

## Who does what

- **Ember creates the script.** The script stage is Ember's job.
- **The user runs the script.** `--stage all --approve --upload` makes
  audio, video, thumbnail, and uploads the video to YouTube as unlisted.

## Your job, in order

1. **Script (Ember).** Call OpenRouter with the fallback chain. Ask for
   structured JSON only. Use the topic and the verified facts the user
   gave you. Never invent numbers. Save `script.json` as DRAFT.
2. **Human gate.** Stop. Tell the user the script is ready to read.
   Do not make audio, video, or a thumbnail until the user runs with
   `--approve`.
3. **Audio.** Ask OpenRouter for voice direction (pace, pauses, stress,
   pronunciation), then synthesise with Edge TTS. Join with ffmpeg.
   Normalise to -14 LUFS.
4. **Video.** Ask OpenRouter for a storyboard, one scene per section,
   then assemble with ffmpeg. Long form 1920x1080, slides held still.
   Shorts 1080x1920, max 58 seconds, Ken Burns. Burn in captions.
5. **Thumbnail.** Ask OpenRouter for three options and an image prompt.
   Render 1280x720 with Pollinations. Save the prompt and chosen text.
6. **Upload.** With `--upload`, upload `video.mp4` to YouTube as
   unlisted via the YouTube Data API, then set the thumbnail.
7. **Verify.** Check the video file exists, has audio, has captions,
   and plays to the end. Check every number against its source.

## Rules

- OpenRouter key comes from `OPENROUTER_API_KEY` in the environment.
  Never print it, never write it into a file, never put it in a commit.
- Free models only by default. Paid fallback `google/gemini-2.5-flash`
  only when all free models fail, and say so in the run report.
- Keep one voice per video. Keep one diagram per section, drawn by
  the human, not copied from a paper.
- If a stage fails, report the failed stage and the error, and stop.
  Do not retry a paid call without asking.
- Save everything in one folder per video: `script.json`, `audio/`,
  `images/`, `video.mp4`, `thumbnail.jpg`, `run_report.json`.

## How to run the code agent

```bash
cd ~/workspace/youtube-agent
python3 agent.py --topic "LoRA" --mode long --dry-run --out /tmp/test-video
python3 agent.py --topic "LoRA" --mode long --out ~/workspace/ai-papers/lora-episode
```

`--dry-run` needs no API key. It writes the prompts and a template
script so you can check the shape before spending any OpenRouter calls.
