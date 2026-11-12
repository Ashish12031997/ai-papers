# OpenRouter free models — verified live 2026-11-12

Free tier: 20 requests per minute, 50 requests per day, or 1000 per day
after a one-time $10 lifetime purchase. No card needed to start.
Only IDs ending in `:free` are $0. Check the live list before every run:
`GET https://openrouter.ai/api/v1/models`

Verified free on 2026-11-12 (13 models):
- nvidia/nemotron-3-ultra-550b-a55b:free
- nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
- nvidia/nemotron-3.5-super-vl:free
- nvidia/nemotron-3.5-lightning:free
- google/gemma-4-26b-a4b-it:free
- google/gemma-4-31b-it:free
- baidu/ernie-5.5-flash-preview:free
- thinkingmachines/inkling-2-small:free
- liquid/lfm-3-1.7b:free
- liquid/lfm-2.5-2.6b:free
- dots-studio/dots-3-note-preview:free
- recursive/flint-v1.0:free
- cohere/north-mini-code:free

Fallback chain to try in order:
1. nvidia/nemotron-3-ultra-550b-a55b:free
2. google/gemma-4-31b-it:free
3. google/gemma-4-26b-a4b-it:free
4. nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free
5. baidu/ernie-5.5-flash-preview:free

Paid fallback, pennies only: google/gemini-2.5-flash, about $0.01 per script.
Do not use DeepSeek R1, Qwen3 Coder 480B, or Llama 3.3 70B as free models.
They were free in older guides and are paid now.
