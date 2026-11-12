# Script format — structured JSON from the LLM

Ask the LLM to return only this JSON, no extra text.

{
  "title": "Problem — How X Fixes It",
  "hook": "70 words, problem in a real example, no paper title yet",
  "sections": [
    {"name": "The Problem", "words": 300, "narration": "...", "visual": "slide or diagram to draw"},
    {"name": "Why old fixes fail", "words": 100, "narration": "...", "visual": "..."},
    {"name": "The Paper Idea", "words": 400, "narration": "...", "visual": "one diagram, redrawn"},
    {"name": "Sample Code", "words": 350, "narration": "...", "visual": "Colab screen record, pause on 3 lines"},
    {"name": "Results and Limits", "words": 200, "narration": "...", "visual": "one table, one number with baseline"},
    {"name": "Takeaway", "words": 70, "narration": "...", "visual": "one sentence on screen"}
  ],
  "description": "YouTube description with paper link, code link, timestamps",
  "tags": ["tag1", "tag2", "tag3"],
  "thumbnail_options": ["option 1 text", "option 2 text", "option 3 text"]
}

Rules:
- Total narration about 1300 words for long form, about 150 words for a Short.
- Every number must come from the facts you gave the LLM, never invented.
- One visual per section, described in words, so the editor can draw it.
- For a Short, return only hook, one idea section, and takeaway.
