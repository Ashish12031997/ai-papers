# Episode 01 — Fine-tuning Is Too Expensive — How LoRA Fixes It

**Paper:** Hu et al. (2021), "LoRA: Low-Rank Adaptation of Large Language Models",
arXiv 2106.09685 — https://arxiv.org/abs/2106.09685
**Demo:** `demo.py` in this folder (49 lines, GPT-2 + PEFT, runs in free Colab)
**Length:** 9–11 minutes, ~1,300 words. Status: DRAFT script — verify the demo
runs in Colab before recording.

---

## 0:00 Hook (~70 words)

Imagine you buy a giant cookbook — every recipe in the world, thousands
of pages. Now you want it to cook *your* family's food, your way. The
obvious way is to rewrite the whole book, page by page. That would take
months, cost a fortune, and you'd need a second copy of the book for
every style you want. That is exactly what fine-tuning a big AI model
used to feel like. This paper fixes it — with a trick so small you can
write it on a sticky note.

## 0:30 The Problem (~300 words)

A large language model is a machine that has read an enormous amount of
text and learned patterns from it — which word usually follows which.
When a company wants that model to do *their* job — answer their
customers, write in their style, follow their rules — they fine-tune it.
Fine-tuning means showing the model examples of the new job and letting
it adjust itself until it gets good at it.

Here is the catch. Adjusting itself means changing its weights. A
weight is just a number the model uses to decide things — think of it
as one tiny dial. A big model has billions of dials. GPT-3, the model
this paper uses as its example, has 175 billion of them.

Full fine-tuning turns *every single dial*. All 175 billion. That means
you need a copy of the whole model for every job you fine-tune it for —
one copy for customer support, another for legal summaries, another for
your language — and each copy is hundreds of gigabytes. You need very
expensive computers with huge memory just to hold it while it trains,
and training takes a long time because there is so much to change.

So in practice, only big companies with big computer budgets could
fine-tune the biggest models. Everyone else had two bad choices: use
the model as it is, even if it does not fit their job, or use a much
smaller model that fits their budget but is not as smart. That is the
problem: adapting a great model was too expensive for almost everyone.

## 2:30 Why old fixes fail (~100 words)

People had tried shortcuts before. One was adapters: bolt small extra
pieces onto the model and train only those pieces. It worked, but the
extra pieces stayed in the model forever, so every answer got a little
slower. Another was prompt tuning: train a few special input words
instead of the model itself. Cheap, but it often performed worse, and
it eats up space in the model's input every time you use it. What was
needed was a fix that was cheap to train, cost nothing at run time,
and performed as well as changing everything.

## 3:00 The Paper Idea (~400 words)

The paper is called LoRA — short for Low-Rank Adaptation — published
in 2021 by Edward Hu and colleagues at Microsoft. Here is the one
trick, in plain English.

Freeze the big model completely. Do not touch a single one of its
175 billion dials. Instead, next to each layer of the model, add two
tiny matrices — think of them as two small tables of numbers, called
A and B. You train *only* those two small tables. Everything else
stays frozen.

Why two tables, and why does that work? Picture the change you want
to make to the model as a huge sheet of numbers — one change for every
connection in a layer. That sheet is enormous. But the paper's insight
is that the *useful* part of that change is actually simple. It can
be described with far fewer numbers than the full sheet. In maths
this is called low rank — rank just means how many independent
directions of change there really are, and for fine-tuning, that
number is small.

So instead of learning the whole huge sheet, you learn A, a tall thin
table, and B, a short wide table. Multiply them together and you get
a change that is the right shape to nudge the frozen layer — but you
only had to learn the numbers in those two small tables. In our demo
we use a rank of 8. That is the size of the small tables, and it is
tiny compared with the layer they are nudging.

And here is the beautiful part. When training is done, you multiply
A and B together and add the result straight into the frozen weights.
The two little tables disappear into the model. The finished model
is exactly the same shape and size as the original — no extra pieces,
no extra work when it answers. That is why, unlike adapters, LoRA
adds no extra delay when the model runs.

One more everyday picture. Think of the frozen model as a printed
textbook. Full fine-tuning rewrites the whole book. LoRA leaves the
book alone and writes your changes on a few sticky notes — then, when
you are happy with them, the notes are printed cleanly into a new
edition of the same book. Same book, same size, now yours.

## 6:00 Sample Code (~350 words + screen)

Now let's see it run — 49 lines, in free Colab, no API key. The file
is `demo.py` in this folder, and the link is in the description.

First, we load GPT-2, a small model with 124 million weights. Small
enough for free Colab, big enough to show the idea. The code counts
its weights and prints them: full fine-tuning would have to train all
124 million.

Then come the three lines that *are* the idea — pause on these on
screen:

First, `LoraConfig(r=8, lora_alpha=16, ...)`. This says: use rank 8 —
those small tables I just described — and target the attention layers,
the parts of the model that decide what to pay attention to.

Second, `get_peft_model(base, config)`. This freezes the base model
and attaches the tiny LoRA tables. From this line on, the big model
cannot change. Only the small tables can learn.

Third, `model.print_trainable_parameters()`. This prints the punchline:
about 0.24 percent of the weights are now trainable. Under one in
four hundred. That is the whole paper in one number on your screen.

Then we run one tiny training step on two short sentences — "The
capital of France is Paris" and "The capital of Japan is Tokyo" — just
to prove the training loop runs and only the LoRA weights move. Be
honest on camera here: one step on two sentences teaches the model
almost nothing. This is a toy demo. It exists to make the mechanism
visible — frozen base, tiny trainable update — not to show a quality
gain. A real fine-tune uses hundreds or thousands of examples.

Finally, we ask the model to finish a sentence — "The capital of
France is" — and it answers, proving the wrapped model still works
after its LoRA update.

## 9:00 Results and Limits (~200 words)

So does it actually work as well as changing everything? On the
paper's own numbers, yes. Compared with fully fine-tuning GPT-3
with Adam, LoRA trains 10,000 times fewer parameters and uses about
3 times less GPU memory — and matches or beats full fine-tuning on
RoBERTa, DeBERTa, GPT-2 and GPT-3. And because the update merges
back into the model, there is no extra delay when it answers.

But know the limits. LoRA does not make a bad base model good — if
the frozen model cannot do the job at all, small nudges will not save
it. Picking the rank is a judgement call: too small and the model
cannot learn enough; too big and you lose the savings. And our demo
is a toy — one step proves the mechanism, it does not prove the model
got smarter. If you fine-tune for real, you need real data, and you
need to check the result on examples the model has never seen.

Who should use it? Anyone who wants a big model to do their specific
job without a big computer budget — that is most of us. Who should
not? Anyone who needs the model to learn something entirely new,
from scratch. LoRA adapts what a model already knows; it does not
teach it a new world.

## 10:30 Takeaway and Next (~70 words)

One sentence to remember: freeze the giant, train a tiny nudge, then
fold the nudge back in — you get a custom model for a fraction of
the cost, with no extra delay.

Next episode: the model still makes things up, because its knowledge
is frozen in time. The paper that fixes that is RAG — Retrieval-Augmented
Generation — and we will run that one in code too.

---

## On-screen checklist (for recording)

- [ ] Hook: cookbook analogy, no paper title in first 20 seconds
- [ ] Diagram to draw yourself: frozen layer + two small tables A and B,
      arrow showing their product merging back into the layer
- [ ] Screen record: Colab run of `demo.py`, pause on the 3 lines above,
      show the ~0.24% trainable-parameters printout
- [ ] Numbers on screen, all from the paper: 10,000x fewer trainable
      parameters, 3x less GPU memory, no extra inference latency
- [ ] Say the toy-demo caveat out loud before the generation step
- [ ] Description links: paper https://arxiv.org/abs/2106.09685,
      official code https://github.com/microsoft/LoRA,
      demo in the ai-papers repo
