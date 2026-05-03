import json
from pathlib import Path

DATA_DIR = Path("data")
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


def main():
    models = json.loads((DATA_DIR / "models.json").read_text(encoding="utf-8"))
    lines = ["# Model Strength Cards\n"]
    for model in models:
        lines.append(f"## {model['model_id']}\n")
        lines.append(f"- Provider: {model['provider']}\n")
        lines.append(f"- Family: {model['family']}\n")
        lines.append(f"- Primary track: {model['primary_track']}\n")
        lines.append(f"- Notes: {model.get('notes', '')}\n")
    out = RESULTS_DIR / "model_strength_cards.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
