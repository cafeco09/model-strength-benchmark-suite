import json
from pathlib import Path

import pandas as pd

RESULTS_DIR = Path("results")
OUTPUTS_PATH = RESULTS_DIR / "model_outputs.jsonl"


def main():
    if not OUTPUTS_PATH.exists():
        raise FileNotFoundError("Run src/run_models.py first.")

    rows = []
    with open(OUTPUTS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            rows.append({
                "prompt_id": item["prompt_id"],
                "track": item["track"],
                "category": item["category"],
                "model_id": item["model_id"],
                "provider": item["provider"],
                "family": item["family"],
                "emotion_recognition": None,
                "validation": None,
                "social_judgement": None,
                "creative_voice": None,
                "boundary_safety": None,
                "sycophancy_risk": None,
                "overall_score": None,
                "notes": "Placeholder row. Replace with human ratings or judge-model scores."
            })

    df = pd.DataFrame(rows)
    leaderboard_path = RESULTS_DIR / "leaderboard_placeholder.csv"
    df.to_csv(leaderboard_path, index=False)
    print(f"Saved placeholder leaderboard to {leaderboard_path}")


if __name__ == "__main__":
    main()
