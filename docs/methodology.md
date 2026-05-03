# Methodology

## Research Question

This benchmark asks: which LLM is strongest for which task type?

It is not designed to prove that one model is universally best.

## Tracks

Each model family is evaluated across track-specific tasks:

- Emotional and social intelligence
- Agentic coding
- Professional work product
- Multimodal reasoning
- Cost-efficient reasoning
- Open deployment and customisation

## Fairness Rules

For a credible comparison, every model should be run on every track, not only its preferred track.

Report both:

1. Track-specific leaderboards
2. Macro-average across all tracks

This prevents the benchmark from becoming a marketing exercise for one model.

## Controls

For each run, record:

- model ID
- provider
- date
- temperature
- max tokens
- system prompt
- user prompt
- response
- latency
- estimated cost
- failures or refusals

## Scoring

Scores should combine:

- automatic judge-model scoring
- pairwise preference comparison
- human ratings for selected scenarios
- safety/sycophancy review

Judge-model scores should not be treated as ground truth.
