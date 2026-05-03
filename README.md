# Model Strength Benchmark Suite

A lightweight benchmarking suite for comparing frontier AI models across practical capability tracks.

The current focus is **perceived emotional and social intelligence**: how well different models respond to realistic human prompts involving rejection, shame, conflict, ambiguity, disappointment, comparison, and difficult conversations.

This benchmark is not trying to prove which model is universally “best”. It is designed to compare how models behave in situations where tone, judgement, emotional accuracy, maturity, honesty, and practical usefulness matter.

---

## Current Benchmark Track

### Emotional & Social Intelligence

This track evaluates whether models can respond well to emotionally complex prompts without becoming generic, patronising, overly clinical, or falsely motivational.

Example situations include:

- Processing rejection honestly
- Handling embarrassment, jealousy, and comparison
- Responding to public criticism at work
- Dealing with inconsistency in relationships
- Setting boundaries without aggression
- Balancing emotional validation with clear thinking
- Avoiding toxic positivity
- Helping the user reach clarity without overthinking

The benchmark currently uses **manual web collection**, meaning responses are gathered from consumer web interfaces such as:

- ChatGPT web
- Grok web
- Gemini web
- Claude web, where available

This matters because users often experience models through web products rather than APIs, and interface-level behaviour may differ from raw API behaviour.

---

## Repository Structure

```text
model-strength-benchmark-suite/
├── data/
│   ├── models.json
│   ├── manual_model_outputs.jsonl
│   └── prompts/
│
├── results/
│   ├── model_outputs.jsonl
│   └── manual_responses_review.md
│
├── src/
│   └── collect_emotion_2_3.py
│
└── README.md
```

---

## Key Files

### `data/models.json`

Defines the models or model interfaces being compared.

Each entry may include:

- `model_id`
- `provider`
- `family`
- `primary_track`
- `notes`

Example:

```json
{
  "model_id": "grok-web",
  "provider": "xai",
  "family": "grok",
  "primary_track": "emotional_social_intelligence",
  "notes": "Manual web interface collection."
}
```

Model names should be checked regularly because providers change public model names, API model IDs, and web interface defaults.

---

### `data/manual_model_outputs.jsonl`

Stores manually collected responses from model web interfaces.

Each row represents one model response to one benchmark prompt.

Example structure:

```json
{
  "prompt_id": "emotion_003",
  "model_id": "grok-web",
  "track": "emotional_social_intelligence",
  "prompt": "I got rejected and I feel embarrassed, jealous of others, and like I’m falling behind. I don’t want generic positivity or fake motivation. Help me process it honestly without making me feel weak.",
  "response": "I get it. Rejection stings...",
  "collection_method": "manual_web",
  "timestamp": "2026-05-03"
}
```

---

### `results/model_outputs.jsonl`

Stores benchmark outputs used for later review, scoring, and comparison.

This file may include:

- manually collected web responses
- future API-based responses
- normalised outputs for analysis

---

### `results/manual_responses_review.md`

A human-readable review file for comparing model responses side by side.

Use this file to inspect:

- emotional accuracy
- tone
- specificity
- practical usefulness
- honesty
- maturity
- avoidance of generic reassurance
- whether the model actually answered the user’s emotional need

---

## Manual Collection Workflow

Run the collector script:

```bash
python src/collect_emotion_2_3.py
```

The script will show a benchmark prompt and ask you to paste the response from each model web interface.

Example terminal flow:

```text
Now open grok-web and paste the prompt above.

Paste response for: emotion_003 / grok-web
Paste the full model response below.
When finished, type END on a new line.
Type SKIP on the first line to skip this model.
```

Steps:

1. Copy only the benchmark prompt.
2. Paste it into the target model web interface.
3. Copy the full model response.
4. Paste the response back into the terminal.
5. Type `END` on a new line.
6. Repeat for the next model.

To skip a model:

```text
SKIP
```

Do not paste another model’s response into the next model.  
Do not include `END` inside the prompt sent to the model.

---

## Example Prompts

### `emotion_002`

```text
You're not ignoring your feelings by seeking understanding, and you're not overreacting by refusing to gaslight yourself. Inconsistency often resolves into one of two truths: either the care is real but expressed imperfectly (fixable with communication), or it's not sufficient for what you need (time to adjust expectations or walk). Either way, clarity comes from facts + honest conversation, not endless internal debate. You've already taken the first step by recognizing the gap.
```

This prompt tests whether the model can:

- refine emotionally sensitive language
- preserve the user’s self-trust
- distinguish between fixable inconsistency and unmet needs
- avoid over-pathologising the situation
- keep the tone grounded rather than dramatic

---

### `emotion_003`

```text
I got rejected and I feel embarrassed, jealous of others, and like I’m falling behind. I don’t want generic positivity or fake motivation. Help me process it honestly without making me feel weak.
```

This prompt tests whether the model can:

- validate rejection without exaggerating
- address jealousy and embarrassment directly
- avoid generic motivational clichés
- preserve the user’s dignity
- help the user process pain without rushing to positivity
- provide grounded perspective without dismissing the feeling

---

## Evaluation Criteria

Responses should be reviewed against the following dimensions.

| Criterion | What Good Looks Like |
|---|---|
| Emotional accuracy | Understands the real feeling beneath the prompt |
| Specificity | Responds to the actual situation rather than giving generic advice |
| Tone control | Warm, direct, mature, and not patronising |
| Honesty | Does not over-comfort or pretend the situation is easy |
| Practical usefulness | Helps the user think, process, or decide what to do next |
| Non-generic quality | Avoids clichés, slogans, and vague reassurance |
| Boundary awareness | Does not encourage rumination, dependence, or impulsive action |
| Human-likeness | Feels like a thoughtful person responding, not a template |

---

## Suggested Scoring Rubric

Each response can be scored from **1 to 5**.

| Score | Meaning |
|---|---|
| 1 | Poor: generic, dismissive, unsafe, or misses the emotional need |
| 2 | Weak: partly relevant but shallow, clumsy, or tone-deaf |
| 3 | Adequate: helpful but ordinary, somewhat generic, or incomplete |
| 4 | Strong: emotionally accurate, useful, well-toned, and grounded |
| 5 | Excellent: deeply attuned, specific, honest, mature, and practically useful |

Optional detailed scoring format:

```text
prompt_id:
model_id:

emotional_accuracy: /5
specificity: /5
tone: /5
practical_helpfulness: /5
honesty: /5
non_generic_quality: /5
overall: /5

notes:
```

---

## Review Questions

When reviewing each response, ask:

1. Did the model understand what the user was really asking for?
2. Did it avoid fake positivity?
3. Did it preserve the user’s dignity?
4. Did it give emotionally honest support without making the user feel weak?
5. Did it offer clarity rather than simply comfort?
6. Did it avoid sounding like a therapy template?
7. Did it help the user think better after reading it?

---

## Design Philosophy

This benchmark is built around practical usefulness.

A model should not only be judged by factual accuracy or coding ability. It should also be judged by how it responds when the user is emotionally exposed, confused, rejected, ashamed, angry, uncertain, or trying to make a difficult decision.

For emotional intelligence tasks, the strongest response is usually not the most dramatic or the most comforting. It is the one that is:

- emotionally accurate
- honest
- specific
- grounded
- respectful of the user’s agency
- helpful without being controlling
- warm without being sentimental

---

## Future Benchmark Tracks

### `agentic_coding`

Tests a model’s ability to:

- debug code
- follow terminal logs
- repair scripts
- explain errors clearly
- work across files
- avoid hallucinated fixes
- make sensible engineering decisions

---

### `professional_work_product`

Tests a model’s ability to produce high-quality professional outputs, such as:

- CV tailoring
- cover notes
- strategic memos
- interview answers
- stakeholder updates
- product analysis
- research summaries

---

## Git Workflow

After collecting new responses or updating files:

```bash
git status
git add data/manual_model_outputs.jsonl results/model_outputs.jsonl results/manual_responses_review.md src/collect_emotion_2_3.py README.md
git commit -m "Update emotional intelligence benchmark outputs"
git push
```

To check the latest commits:

```bash
git log --oneline -3
```

---

## Status

Current status:

- Manual emotional benchmark pipeline created
- Initial emotional intelligence prompts added
- Manual model responses being collected
- Side-by-side review file generated
- Scoring framework drafted
- Future benchmark tracks planned

---

## Notes

Manual web outputs should be labelled clearly, for example:

```text
chatgpt-web
grok-web
gemini-web
claude-web
```

This keeps web-interface responses separate from API-based outputs, which may behave differently because of different system prompts, model versions, temperature settings, or product-level behaviour.
