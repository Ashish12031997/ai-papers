# Attention Is All You Need — tiny demo, in plain sight
# Paper: Vaswani et al. (2017), arXiv 1706.03762
# Idea: scaled dot-product attention. Every word gets a Query, a Key
# and a Value. Compare Queries with Keys, turn the scores into weights,
# then mix the Values with those weights. That is it.
# Run:  python demo.py   (NumPy only, no GPU, no API key)
# Note: the embeddings here are random (fixed seed), not learned, so
# the attention pattern is a sketch of the mechanism, not a real model.

import numpy as np

np.random.seed(1)
words = ["the", "cat", "sat", "on", "the", "mat"]
d = 8  # tiny size, so the numbers stay readable

# --- 1. Each word gets a small list of numbers (its embedding) ---
X = np.random.randn(len(words), d)

# --- 2. Make Q, K and V: the same numbers, three different lenses ---
Wq, Wk, Wv = (np.random.randn(d, d) * 0.5 for _ in range(3))
Q, K, V = X @ Wq, X @ Wk, X @ Wv

# --- 3. Scores: how much does each Query match each Key? ---
scores = Q @ K.T / np.sqrt(d)
weights = np.exp(scores - scores.max(axis=1, keepdims=True))
weights /= weights.sum(axis=1, keepdims=True)  # softmax: rows add to 1

# --- 4. Mix the Values with those weights: the new meaning ---
out = weights @ V

print("Attention weights — rows are the word asking, columns are the word it looks at:\n")
print("        " + "  ".join(f"{w:>5}" for w in words))
for w, row in zip(words, weights):
    print(f"{w:>5}  " + "  ".join(f"{v:.2f}" for v in row))
print("\nMost attention paid by 'sat':", words[int(np.argmax(weights[2]))])
print("Done. Q, K, V -> scores -> weights -> mix. That is attention.")
