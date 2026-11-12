# Episode 01 — LoRA: Low-Rank Adaptation of Large Language Models

**Paper:** Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang & Chen (2021),
arXiv 2106.09685 — https://arxiv.org/abs/2106.09685
**Official code:** https://github.com/microsoft/LoRA

## The problem (one sentence)

Fine-tuning a big language model normally means retraining *every*
weight — for GPT-3 that is 175 billion weights per copy, which is
too expensive and too slow for most people to do at all.

## The trick (one sentence)

Freeze the big model completely, and train only two tiny side-matrices
(A and B) per layer whose product nudges the frozen weights — a
"low-rank update" with far fewer numbers to learn.

## Why it matters (numbers from the paper itself)

- vs GPT-3 175B fine-tuned with Adam: LoRA cuts trainable parameters
  by **10,000x** and GPU memory needed by **3x**.
- Quality is on par or better than full fine-tuning on RoBERTa,
  DeBERTa, GPT-2 and GPT-3 — despite training far less.
- Unlike adapter methods, LoRA adds **no extra inference latency**:
  after training, the small update merges back into the frozen weights.

## What the demo shows

`demo.py` (49 lines) loads GPT-2 (124M weights, small enough for free
Colab) and does the whole idea in four steps:

1. Counts the base model's weights — full fine-tuning would move all of them.
2. Wraps it in LoRA (`r=8`, on the attention layers) and prints how few
   weights are now trainable — about 0.24% of the model.
3. Runs one tiny training step on two short sentences, to prove the
   training loop runs and only the LoRA weights move.
4. Generates a completion, to prove the wrapped model still works.

This is a toy demo, not a real fine-tune: one step on two sentences
teaches the model almost nothing. It exists to make the *mechanism*
visible — frozen base + tiny trainable update — not to show a quality gain.

## How to run in Google Colab

1. Open https://colab.research.google.com, upload `demo.py`
   (or open it from GitHub once pushed).
2. Run this first:
   ```
   !pip install transformers peft torch accelerate
   ```
3. Run:
   ```
   !python demo.py
   ```
   First run downloads GPT-2 (~500 MB). No API key needed.
   Runs on free Colab CPU or GPU in a couple of minutes.

## Links

- Paper: https://arxiv.org/abs/2106.09685
- Official code: https://github.com/microsoft/LoRA
- Demo: `demo.py` in this folder
