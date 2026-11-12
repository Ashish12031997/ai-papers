# AI Papers, Explained Simply

Every paper solves a problem. Start with the problem in plain English,
then the paper's idea, then run the code.

YouTube channel by Ashish Patadiya — learn-in-public, for non-tech
people and junior devs who have heard a paper name but never read it.

## Format — Problem, Paper, Code

1. **The Problem** — why is this hard, what fails today?
2. **The Paper** — the one trick, in plain English, one diagram redrawn
3. **Sample Code** — 30-50 lines in Colab, input -> output, live

8-12 minutes per episode, 16:9. No jargon without a 5-second translation.

## Episodes

| # | Paper | Problem | Status |
|---|-------|---------|--------|
| 01 | LoRA (2106.09685) | Fine-tuning is too expensive | Script written, demo building |
| 02 | RAG (2005.11401) | LLMs hallucinate / frozen knowledge | Planned |
| 03 | Attention Is All You Need (1706.03762) | RNNs are slow, forget long text | Planned |
| 04 | Chain-of-Thought (2201.11903) | LLMs fail multi-step reasoning | Planned |
| 05 | FlashAttention (2205.14135) | Attention eats GPU memory | Planned |

Full plan: see `ai-papers-channel-plan.md` in the workspace.

## Repo structure

```
ai-papers/
  lora-episode/
    README.md      — problem, trick, links, how to run
    demo.py        — minimal runnable demo, 30-50 lines
    script.md      — video script, Problem -> Paper -> Code
    slides/        — your own diagrams, not paper figures
  youtube-agent/
    agent.py       — run it: script (Ember) -> audio/video/thumbnail -> YouTube upload (you)
    README.md      — setup and run instructions
  skills/
    youtube-video-creator-openrouter/ — skill the agent follows
```

## Making a video — many shorts, merged into one

Ember creates the script. You run the agent and it makes the video
and uploads it as unlisted.

```bash
pip install -r youtube-agent/requirements.txt
export OPENROUTER_API_KEY=sk-or-...
# 1. Script (Ember's job, DRAFT, stops at the human gate)
python3 youtube-agent/agent.py --topic "LoRA" --mode long --out lora-episode
# 2. Read lora-episode/script.json, approve it, then run everything
python3 youtube-agent/agent.py --topic "LoRA" --mode long --out lora-episode --stage all --approve --upload
```

Smart part: the script is split into segments of at most 150 words
(~70 seconds each). Each segment is rendered on its own as a short
clip, then all segments are merged with ffmpeg concat into `video.mp4`.
A failed segment is re-rendered alone with `--segment segment-03`.
Each segment is also a ready Short on its own. Upload needs a
one-time YouTube OAuth setup (`client_secrets.json`, see
`youtube-agent/README.md`).

## How to run a demo

Open `demo.py` in Google Colab, run all cells. No API keys needed
for the minimal demos. Links to the official paper repo are in each
episode README.

## Rules

- Read the paper yourself. LLM summaries are a first pass only.
- Verify every number against the paper's table.
- Redraw diagrams, do not screenshot paper figures.
- Code must run in Colab in under 5 minutes, or pick a smaller demo.
