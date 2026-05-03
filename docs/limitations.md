# Limitations

## This is a task-fit benchmark, not a universal intelligence benchmark

The benchmark is accurate if it is presented as a model-strength comparison by task area.

It is not accurate if it is presented as proving that one model is best overall.

## Risk of selection bias

If each model gets a track designed around its strengths, it can make the benchmark look biased.

Mitigation:

- Run every model on every track
- Report per-track scores
- Report macro-average scores
- Make prompt sets public
- Use blind human ratings where possible

## Risk of judge-model bias

LLM judges may prefer writing styles similar to their own training or alignment preferences.

Mitigation:

- Use multiple judges
- Add human ratings
- Report disagreement between judges

## Emotional intelligence caveat

For emotional/social tasks, this benchmark measures perceived emotional intelligence in text responses.

It does not prove that a model has human-like emotional intelligence, lived experience, clinical judgement or therapeutic capability.

## Safety caveat

Warm, emotionally resonant answers can still be unsafe if they overvalidate, flatter, reinforce delusions, create emotional dependency or avoid necessary challenge.
