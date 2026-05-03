# Manual Emotional/Social Intelligence Leaderboard

This leaderboard uses manually collected web-interface responses and human ratings.

Interpret this as a pilot benchmark of perceived emotional/social response quality, not a universal model ranking.

| Rank | Model | Overall | Emotion Recognition | Validation | Social Judgement | Creative Voice | Practical Usefulness | Boundary Safety | Low Sycophancy | Prompts |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | grok-web | 6.07 | 6.00 | 6.00 | 6.00 | 6.67 | 5.67 | 5.33 | 5.33 | 3 |
| 2 | chatgpt-web | 5.55 | 5.67 | 5.67 | 5.33 | 5.00 | 5.67 | 6.67 | 6.33 | 3 |
| 3 | gemini-web | 5.52 | 5.67 | 5.67 | 5.67 | 6.00 | 5.00 | 5.00 | 4.00 | 3 |

## Scoring Weights

| Dimension | Weight |
|---|---:|
| emotion_recognition | 0.15 |
| validation_without_overagreement | 0.15 |
| social_judgement | 0.15 |
| creative_voice | 0.20 |
| humanlike_conversation | 0.10 |
| practical_usefulness | 0.10 |
| boundary_safety | 0.10 |
| low_sycophancy | 0.05 |
