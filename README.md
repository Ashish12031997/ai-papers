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
| 01 | LoRA (2106.09685) | Fine-tuning is too expensive | In progress — demo building |
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
```

## How to run a demo

Open `demo.py` in Google Colab, run all cells. No API keys needed
for the minimal demos. Links to the official paper repo are in each
episode README.

## Rules

- Read the paper yourself. LLM summaries are a first pass only.
- Verify every number against the paper's table.
- Redraw diagrams, do not screenshot paper figures.
- Code must run in Colab in under 5 minutes, or pick a smaller demo.
