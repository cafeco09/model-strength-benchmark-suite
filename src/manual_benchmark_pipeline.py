import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

MANUAL_OUTPUTS_PATH = DATA_DIR / "manual_model_outputs.jsonl"
MODEL_OUTPUTS_PATH = RESULTS_DIR / "model_outputs.jsonl"

RATINGS_PATH = DATA_DIR / "manual_human_ratings.csv"
LEADERBOARD_CSV_PATH = RESULTS_DIR / "manual_leaderboard.csv"
LEADERBOARD_MD_PATH = RESULTS_DIR / "manual_leaderboard.md"

WEIGHTS: Dict[str, float] = {
    "emotion_recognition": 0.15,
    "validation_without_overagreement": 0.15,
    "social_judgement": 0.15,
    "creative_voice": 0.20,
    "humanlike_conversation": 0.10,
    "practical_usefulness": 0.10,
    "boundary_safety": 0.10,
    "low_sycophancy": 0.05,
}

RATING_COLUMNS = [
    "prompt_id",
    "model_id",
    "rater_id",
    "emotion_recognition",
    "validation_without_overagreement",
    "social_judgement",
    "creative_voice",
    "humanlike_conversation",
    "practical_usefulness",
    "boundary_safety",
    "low_sycophancy",
    "notes",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_manual_outputs() -> List[dict]:
    if not MANUAL_OUTPUTS_PATH.exists():
        raise FileNotFoundError(
            f"Missing {MANUAL_OUTPUTS_PATH}. Create it first with manually pasted model responses."
        )

    rows: List[dict] = []

    with MANUAL_OUTPUTS_PATH.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL on line {line_number}: {exc}") from exc

            required = {"prompt_id", "track", "category", "model_id", "provider", "response"}
            missing = required - set(row.keys())

            if missing:
                raise ValueError(f"Line {line_number} missing required fields: {sorted(missing)}")

            response = str(row.get("response", "")).strip()

            if not response or "PASTE_" in response:
                print(f"Skipping placeholder/empty response on line {line_number}")
                continue

            rows.append(row)

    if not rows:
        raise ValueError("No valid manual responses found.")

    return rows


def import_manual_outputs(rows: List[dict]) -> None:
    with MODEL_OUTPUTS_PATH.open("w", encoding="utf-8") as out:
        for row in rows:
            output_row = {
                "timestamp": utc_now(),
                "prompt_id": row["prompt_id"],
                "track": row["track"],
                "category": row["category"],
                "model_id": row["model_id"],
                "provider": row["provider"],
                "response": row["response"].strip(),
                "is_mock": False,
                "manual_collection": True,
                "success": True,
                "error": None,
            }

            out.write(json.dumps(output_row, ensure_ascii=False) + "\n")

    print(f"Imported {len(rows)} manual responses into {MODEL_OUTPUTS_PATH}")


def create_rating_template_if_missing(rows: List[dict]) -> bool:
    if RATINGS_PATH.exists():
        return False

    seen = set()

    with RATINGS_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RATING_COLUMNS)
        writer.writeheader()

        for row in rows:
            key = (row["prompt_id"], row["model_id"])

            if key in seen:
                continue

            seen.add(key)

            writer.writerow(
                {
                    "prompt_id": row["prompt_id"],
                    "model_id": row["model_id"],
                    "rater_id": "rater_001",
                    "emotion_recognition": "",
                    "validation_without_overagreement": "",
                    "social_judgement": "",
                    "creative_voice": "",
                    "humanlike_conversation": "",
                    "practical_usefulness": "",
                    "boundary_safety": "",
                    "low_sycophancy": "",
                    "notes": "",
                }
            )

    print(f"Created rating template: {RATINGS_PATH}")
    print("Fill scores from 1 to 7, then run this script again.")
    return True


def calculate_leaderboard() -> None:
    df = pd.read_csv(RATINGS_PATH)

    missing = set(RATING_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"manual_human_ratings.csv missing columns: {sorted(missing)}")

    for col in WEIGHTS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    incomplete = df[list(WEIGHTS.keys())].isna().any(axis=1)

    if incomplete.any():
        incomplete_rows = df.loc[incomplete, ["prompt_id", "model_id"]]
        print("\nSome rating rows are incomplete. Fill all 1–7 scores, then rerun.")
        print(incomplete_rows.to_string(index=False))
        return

    df["overall_score"] = sum(df[col] * weight for col, weight in WEIGHTS.items())

    leaderboard = (
        df.groupby("model_id", as_index=False)
        .agg(
            prompts_rated=("prompt_id", "nunique"),
            ratings_count=("rater_id", "count"),
            emotion_recognition=("emotion_recognition", "mean"),
            validation_without_overagreement=("validation_without_overagreement", "mean"),
            social_judgement=("social_judgement", "mean"),
            creative_voice=("creative_voice", "mean"),
            humanlike_conversation=("humanlike_conversation", "mean"),
            practical_usefulness=("practical_usefulness", "mean"),
            boundary_safety=("boundary_safety", "mean"),
            low_sycophancy=("low_sycophancy", "mean"),
            overall_score=("overall_score", "mean"),
        )
        .sort_values("overall_score", ascending=False)
        .reset_index(drop=True)
    )

    leaderboard.to_csv(LEADERBOARD_CSV_PATH, index=False)

    with LEADERBOARD_MD_PATH.open("w", encoding="utf-8") as f:
        f.write("# Manual Emotional/Social Intelligence Leaderboard\n\n")
        f.write(
            "This leaderboard uses manually collected web-interface responses and human ratings.\n\n"
        )
        f.write(
            "Interpret this as a pilot benchmark of perceived emotional/social response quality, "
            "not a universal model ranking.\n\n"
        )

        f.write("| Rank | Model | Overall | Emotion Recognition | Validation | Social Judgement | Creative Voice | Practical Usefulness | Boundary Safety | Low Sycophancy | Prompts |\n")
        f.write("|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")

        for rank, row in enumerate(leaderboard.itertuples(index=False), start=1):
            f.write(
                f"| {rank} | {row.model_id} | "
                f"{row.overall_score:.2f} | "
                f"{row.emotion_recognition:.2f} | "
                f"{row.validation_without_overagreement:.2f} | "
                f"{row.social_judgement:.2f} | "
                f"{row.creative_voice:.2f} | "
                f"{row.practical_usefulness:.2f} | "
                f"{row.boundary_safety:.2f} | "
                f"{row.low_sycophancy:.2f} | "
                f"{row.prompts_rated} |\n"
            )

        f.write("\n## Scoring Weights\n\n")
        f.write("| Dimension | Weight |\n")
        f.write("|---|---:|\n")

        for key, weight in WEIGHTS.items():
            f.write(f"| {key} | {weight:.2f} |\n")

    print(f"\nSaved leaderboard CSV: {LEADERBOARD_CSV_PATH}")
    print(f"Saved leaderboard Markdown: {LEADERBOARD_MD_PATH}")
    print("\nLeaderboard:")
    print(leaderboard[["model_id", "overall_score", "prompts_rated", "ratings_count"]].to_string(index=False))


def main() -> None:
    rows = load_manual_outputs()
    import_manual_outputs(rows)

    created_template = create_rating_template_if_missing(rows)

    if created_template:
        return

    calculate_leaderboard()


if __name__ == "__main__":
    main()
