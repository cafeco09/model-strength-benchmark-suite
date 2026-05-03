# Model Strength Benchmark Suite

This project compares leading LLMs by the areas where each model family is expected to be strongest.

Instead of asking:

> Which model is best overall?

This benchmark asks:

> Which model is best for which kind of task?

## Benchmark Tracks

| Track | Main Models Tested | Purpose |
|---|---|---|
| Emotional & Social Intelligence | Grok, Claude, GPT | Emotional resonance, social judgement, expressive support |
| Agentic Coding | Claude, GPT, Qwen, Kimi | Debugging, refactoring, software-agent tasks |
| Professional Work Product | GPT, Claude, Gemini | Business analysis, documents, spreadsheets, presentations |
| Multimodal Reasoning | Gemini, GPT, Claude | Charts, images, screenshots, visual reasoning |
| Open Agentic Reasoning | Kimi, Qwen, DeepSeek | Tool-use, coding, long-context reasoning |
| Cost-Efficient Reasoning | DeepSeek, Qwen, Mistral | Accuracy per cost and latency |
| Open Deployment | Mistral, Llama, Qwen | Local deployment, customisation, licence flexibility |

## Why Grok Gets Its Own Track

Grok is tested on emotionally expressive, creative and socially aware responses because this is where Grok is publicly positioned as a strong candidate.

The Grok-focused track does not claim that Grok is the best model overall. It tests whether Grok performs especially well on:

- emotional resonance
- social judgement
- creative voice
- conversational personality
- real-time social interpretation
- boundary-safe support

## Scoring Philosophy

This benchmark does not use one universal score only. Each model family is evaluated against the task type where it should plausibly perform well.

The final output should include:

1. Leaderboard by track
2. Model strength cards
3. Cost and latency comparison
4. Safety and sycophancy checks
5. Human preference ratings where available

## Status

This repository is currently in the experiment-design stage.

Initial goals:

- [ ] Add prompt datasets
- [ ] Add scoring rubrics
- [ ] Add model runner script
- [ ] Add judge script
- [ ] Add leaderboard generation
- [ ] Add human-rating template
