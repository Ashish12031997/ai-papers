# LoRA in plain English — Episode 01 of AI Papers, Explained Simply
# Paper: Hu et al. (2021), arXiv 2106.09685 — https://arxiv.org/abs/2106.09685
# Problem: fine-tuning GPT-2 normally retrains ALL 124 million weights.
# Trick: FREEZE the big model. Train only two tiny side-matrices (A and B)
#   that nudge each layer. The update is low-rank, so it has far fewer
#   numbers to learn — yet the finished model is the same shape as before.
# Run in Colab first:  !pip install transformers peft torch accelerate
# Then:  python demo.py   (no API key; GPT-2 downloads once, ~500 MB)

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

MODEL = "gpt2"  # small, 124M weights — loads on a free Colab CPU or GPU

# --- 1. Load the base model: count what full fine-tuning would move ---
tokenizer = AutoTokenizer.from_pretrained(MODEL)
tokenizer.pad_token = tokenizer.eos_token
base = AutoModelForCausalLM.from_pretrained(MODEL)
total = sum(p.numel() for p in base.parameters())
print(f"Base model: {total:,} weights. Full fine-tuning trains ALL of them.")

# --- 2. Wrap it in LoRA: freeze everything, add tiny trainable weights ---
config = LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05,
                    target_modules=["c_attn", "c_proj"])
model = get_peft_model(base, config)
model.print_trainable_parameters()  # <-- this number is the whole point

# --- 3. One tiny training step, on two short sentences ---
# Real training uses hundreds of examples. This just proves the loop runs
# and only the LoRA weights move — the frozen base never changes.
texts = ["The capital of France is Paris.",
         "The capital of Japan is Tokyo."]
inputs = tokenizer(texts, return_tensors="pt", padding=True)
model.train()
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
loss = model(**inputs, labels=inputs["input_ids"]).loss
print(f"Training loss after 1 step on toy data: {loss.item():.2f}")
loss.backward()
optimizer.step()

# --- 4. Use it: ask the model to finish a sentence ---
model.eval()
prompt = "The capital of France is"
ids = tokenizer(prompt, return_tensors="pt").input_ids
out = model.generate(ids, max_new_tokens=6,
                     pad_token_id=tokenizer.eos_token_id)
print("Model says:", tokenizer.decode(out[0], skip_special_tokens=True))
print("Done. You trained under 1% of the weights — that is LoRA.")
