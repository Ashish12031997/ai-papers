# Audio and thumbnail

## Audio

- Drafts and Shorts: Edge TTS, free, no key.
  `edge-tts --voice en-US-AndrewNeural --text "..." --write-media out.mp3`
  One voice per video. Split by section, then join with ffmpeg.
- Final, commercial safe: Kokoro 82M local, Apache 2.0, unlimited.
  `pip install kokoro-onnx soundfile`
  Slower on CPU for 10 minutes, fine for Shorts.
- Best voice, monetised only: ElevenLabs Starter, $6 per month.
  Free tier is personal use only, do not use it for a monetised channel.
- Normalise to -14 LUFS. Duck music 11 dB under voice.

## Thumbnail

Ask the LLM for three options, each with:
- 3 to 5 words of text only
- Left side: the problem, in red or stuck
- Right side: the fix, in green or simple
- No shocked face, no red arrow, no claim the video does not prove

Render at 1280 by 720 from the best slide or scene image.
Add large bold text with ffmpeg drawtext or Pillow.
Save the prompt, image source, and chosen text in the run report.

## Video assembly

- Long form: 1920 by 1080, 30 fps, storyboard, slides held still.
- Shorts: 1080 by 1920, max 58 seconds, Ken Burns, karaoke captions.
- Captions: faster-whisper locally, burn in with ASS or SRT.
- Codec: H.264 plus AAC. Upload unlisted first, watch fully, then public.
