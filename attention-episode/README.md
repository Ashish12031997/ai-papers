# Attention Is All You Need — Episode

**Paper:** Vaswani et al. (2017), arXiv 1706.03762 — https://arxiv.org/abs/1706.03762

**Problem:** RNNs read one word at a time, forget the start of long sentences,
and cannot train in parallel.

**Trick:** Self-attention. Every word gets a Query, a Key and a Value.
Compare Queries with Keys, turn the scores into weights, mix the Values.
Eight heads at once, each 64 wide, d_model 512. No recurrence, no convolution.

**Paper numbers (verified vs arXiv 1706.03762):**
- 28.4 BLEU, English→German (WMT 2014 newstest2014), +2.0 over the best previous, ensembles included
- 41.8 BLEU, English→French, best single model at the time (abstract / Table 2; the results text gives 41.0 for the same model — the 41.8 figure is the abstract's)
- Base model: state of the art in ~12 hours on 8 P100 GPUs; big model: 3.5 days on 8 GPUs

## How to run the demo

```bash
python demo.py   # NumPy only, no GPU, no API key, runs in seconds
```

It prints an attention table for "the cat sat on the mat". The embeddings
are random (fixed seed), not learned — the demo shows the mechanism
(Q, K, V → scores → weights → mix), not a trained model.

## Video

Slide/diagram style, 9–11 min, Problem → Paper → Code. Script in `script.md`.
Rendered in segments of max 150 words, merged with ffmpeg concat.
Voice: Muse TTS, Helio. Captions burned in.
