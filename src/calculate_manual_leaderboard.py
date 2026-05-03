import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

RATINGS_PATH = DATA_DIR / "manual_human_ratings.csv"
LEADERBOARD_CSV = RESULTS_DIR / "manual_leaderboard.csv"
LEADERBOARD_MD = RESULTS_DIR / "manual_leaderboard.md"

WEIGHTS = {
    "emotion_recognition": 0.15,
    "validation_without_overagreement": 0.15,
    "social_judgement": 0.15,
    "creative_voice": 0.20,
    "humanlike_conversation": 0.10,
    "practical_usefulness": 0.10,
    "boundary_safety": 0.10,
    "low_sycophancy": 0.05,
}

def main():
    df = pd.read_csv(RATINGS_PATH)

    required = {"prompt_id", "model_id", "rater_id", *WEIGHTS.keys()}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    for col in WEIGHTS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

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
    )

    leaderboard.to_csv(LEADERBOARD_CSV, index=False)

    with LEADERBOARD_MD.open("w", encoding="utf-8") as f:
        f.write("# Manual Emotional/Social Intelligence Leaderboard\n\n")
        f.write("This leaderboard uses manually collected web-interface responses and human ratings.\n\n")
        f.write("Current scope: one workplace-conflict prompt (`emotion_001`). Treat this as a pilot result, not a final benchmark.\n\n")
        f.write("| Rank | Model | Overall | Creative Voice | Practical Usefulness | Boundary Safety | Low Sycophancy | Ratings |\n")
        f.write("|---:|---|---:|---:|---:|---:|---:|---:|\n")

        for rank, row in enumerate(leaderboard.itertuples(index=False), start=1):
            f.write(
                f"| {rank} | {row.model_id} | "
                f"{row.overall_score:.2f} | "
                f"{row.creative_voice:.2f} | "
                f"{row.practical_usefulness:.2f} | "
                f"{row.boundary_safety:.2f} | "
                f"{row.low_sycophancy:.2f} | "
                f"{row.ratings_count} |\n"
            )

    print(f"Saved {LEADERBOARD_CSV}")
    print(f"Saved {LEADERBOARD_MD}")
    print(leaderboard[["model_id", "overall_score"]])

if __name__ == "__main__":
    main()
