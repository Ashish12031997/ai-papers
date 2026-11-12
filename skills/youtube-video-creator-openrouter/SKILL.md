# YouTube Video Creator with OpenRouter

## Choose the OpenRouter model first

- Call `GET https://openrouter.ai/api/v1/models` and keep only IDs ending in `:free` before you pick a model.
- Never hard code one free model, because the free roster changes monthly.
- Try the fallback chain in `references/openrouter-models.md` in order and move to the next model on a 429 error.
- Keep each script call under 2048 output tokens and split a long script into scene chunks.
- Use temperature 0.7 for Shorts and 0.5 to 0.6 for explainers.
- Add a paid fallback only when all free models fail, and say so in the run report.

## Make the script with the LLM

- Ask for structured JSON only, using the schema in `references/script-format.md`.
- Give the LLM the topic, the audience, the length, and the verified facts, and never let it invent numbers.
- Follow the fixed order Problem, Paper, Code for research papers, or Hook, Problem, Idea, Demo, Takeaway for general topics.
- Keep narration near 130 words per minute, about 1300 words for a 9 to 11 minute video and about 150 words for a 60 second Short.
- Stop after the script and wait for the human review gate before you make audio or video.
- Fix the script from the human edit, do not regenerate it from scratch.

## Make the audio with the LLM script

- Split the approved script into sentences and synthesise each section separately, then join them.
- Use Edge TTS for drafts and Shorts, with a single consistent voice per video.
- Use Kokoro 82M local for a commercial safe final when you plan to monetise.
- Use ElevenLabs Starter only when you want the best voice and you are monetising.
- Normalise the joined audio to minus 14 LUFS and duck background music under the voice.
- Check the audio length against the script length and re-record a section when it drifts.

## Make the video with ffmpeg — many shorts, merged into one

- Split the script into segments of at most 150 words, about 70 seconds each.
- Render each segment on its own as a high quality short clip: own audio, own title card, own captions. A failed segment is re-rendered alone, the good ones are never touched.
- Merge all segments with ffmpeg concat into video.mp4. Keep codec and resolution identical across segments so the merge is a stream copy, no re-encode loss.
- Each segment is also a ready Short on its own, same audio with a vertical 1080 by 1920 card.
- Use your own slides and diagrams and a screen recording for code, not AI images for the core explanation.
- Use Pollinations free images or Pexels free stock only for Shorts and B-roll.
- Assemble landscape 1920 by 1080 for long form and portrait 1080 by 1920 for Shorts.
- Hold slides still for explainers and use slow Ken Burns motion for Shorts.
- Burn in captions from the audio with faster whisper and keep them to three words per line for Shorts.
- Render to H264 plus AAC, watch the full render once, then upload as unlisted first.

## Make the thumbnail with the LLM

- Ask the LLM for three thumbnail options using the brief in `references/audio-thumbnail.md`.
- Keep the thumbnail text to three to five words, one problem on the left and one fix on the right.
- Make the thumbnail 1280 by 720 from the best scene image or slide, with large bold text.
- Never use a shocked face, a red arrow, or a claim the video does not prove.
- Save the thumbnail prompt, the image source, and the chosen text in the run report.

## Verify before you publish

- Check every number in the script against its source and link the source in the description.
- Check the video file exists, has audio, has captions, and plays to the end.
- Tick the altered content disclosure when voice or visuals are AI generated.
- Keep the script, audio, images, video, thumbnail, and run report in one folder per video.

## Available connectors

- GitHub at `/opt/hatch/connectors/github/CONNECTOR.md` for pushing episode files.
