import json
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

INPUT_PATH = DATA_DIR / "manual_model_outputs.jsonl"
OUTPUT_PATH = RESULTS_DIR / "model_outputs.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing {INPUT_PATH}")

    rows_written = 0

    with INPUT_PATH.open("r", encoding="utf-8") as f, OUTPUT_PATH.open("w", encoding="utf-8") as out:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL on line {line_number}: {exc}") from exc

            response = row.get("response", "").strip()

            if not response or "PASTE_" in response:
                continue

            output_row = {
                "timestamp": utc_now(),
                "prompt_id": row["prompt_id"],
                "track": row["track"],
                "category": row["category"],
                "model_id": row["model_id"],
                "provider": row["provider"],
                "response": response,
                "is_mock": False,
                "manual_collection": True,
                "success": True,
                "error": None,
            }

            out.write(json.dumps(output_row, ensure_ascii=False) + "\n")
            rows_written += 1

    print(f"Imported {rows_written} manual responses into {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
