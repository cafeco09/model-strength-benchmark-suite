import json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

PROMPT_FILES = [
    DATA_DIR / "prompts_emotional_social.jsonl",
    DATA_DIR / "prompts_professional_work.jsonl",
    DATA_DIR / "prompts_agentic_coding.jsonl",
    DATA_DIR / "prompts_multimodal_reasoning.jsonl",
    DATA_DIR / "prompts_cost_reasoning.jsonl",
]


def load_jsonl(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def mock_model_response(model_id: str, prompt: str) -> str:
    """Placeholder. Replace with real provider calls later."""
    return f"[MOCK RESPONSE from {model_id}] This is where the model output will go for prompt: {prompt[:120]}..."


def main():
    with open(DATA_DIR / "models.json", "r", encoding="utf-8") as f:
        models = json.load(f)

    output_path = RESULTS_DIR / "model_outputs.jsonl"

    with open(output_path, "w", encoding="utf-8") as out:
        for prompt_file in PROMPT_FILES:
            if not prompt_file.exists():
                continue
            for item in load_jsonl(prompt_file):
                for model in models:
                    started_at = datetime.now(timezone.utc).isoformat()
                    response = mock_model_response(model["model_id"], item["prompt"])
                    finished_at = datetime.now(timezone.utc).isoformat()
                    result = {
                        "started_at": started_at,
                        "finished_at": finished_at,
                        "prompt_id": item["prompt_id"],
                        "track": item["track"],
                        "category": item["category"],
                        "risk_level": item["risk_level"],
                        "model_id": model["model_id"],
                        "provider": model["provider"],
                        "family": model["family"],
                        "response": response,
                        "is_mock": True,
                    }
                    out.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"Saved outputs to {output_path}")


if __name__ == "__main__":
    main()
