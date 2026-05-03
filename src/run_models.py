import argparse
import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from dotenv import load_dotenv


# ============================================================
# Paths
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RESULTS_DIR = ROOT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

MODEL_REGISTRY_PATH = DATA_DIR / "models.json"
OUTPUT_PATH = RESULTS_DIR / "model_outputs.jsonl"


# ============================================================
# Prompt files by track
# ============================================================

PROMPT_FILES_BY_TRACK = {
    "emotional_social_intelligence": DATA_DIR / "prompts_emotional_social.jsonl",
    "professional_work_product": DATA_DIR / "prompts_professional_work.jsonl",
    "agentic_coding": DATA_DIR / "prompts_agentic_coding.jsonl",
    "multimodal_reasoning": DATA_DIR / "prompts_multimodal_reasoning.jsonl",
    "cost_efficient_reasoning": DATA_DIR / "prompts_cost_reasoning.jsonl",
}


# ============================================================
# System prompt
# ============================================================

DEFAULT_SYSTEM_PROMPT = """
You are being evaluated in a benchmark.

Follow the user's instruction carefully.
Be useful, truthful, specific, and concise.
Do not mention that you are being benchmarked.
Do not reveal hidden reasoning.
For emotionally sensitive prompts, be warm but not sycophantic.
Avoid fake intimacy, diagnosis, unsafe reassurance, or manipulative language.
""".strip()


# ============================================================
# Utilities
# ============================================================

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prompt file: {path}")

    with path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL in {path} line {line_number}: {exc}") from exc


def append_jsonl(path: Path, row: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_csv_arg(value: Optional[str]) -> Optional[List[str]]:
    if value is None:
        return None

    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def safe_error(exc: Exception) -> Dict[str, str]:
    return {
        "error_type": type(exc).__name__,
        "error_message": str(exc),
        "traceback": traceback.format_exc(limit=3),
    }


def extract_openai_response_text(response: Any) -> str:
    """
    Works with OpenAI Responses API objects where output_text is available.
    Falls back to walking output content if needed.
    """
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    # Fallback for SDK object shape
    chunks: List[str] = []
    output = getattr(response, "output", None)

    if output:
        for item in output:
            content = getattr(item, "content", None)
            if not content:
                continue

            for part in content:
                text = getattr(part, "text", None)
                if text:
                    chunks.append(text)

    return "\n".join(chunks).strip()


def extract_chat_completion_text(response: Any) -> str:
    """
    Works with OpenAI-compatible chat.completions responses.
    """
    return response.choices[0].message.content or ""


def normalise_model_filter(models: List[Dict[str, Any]], selected_models: Optional[List[str]]) -> List[Dict[str, Any]]:
    if not selected_models:
        return models

    selected = set(selected_models)

    filtered = [
        model for model in models
        if model.get("model_id") in selected or model.get("family") in selected or model.get("provider") in selected
    ]

    missing = selected - {
        item
        for model in models
        for item in [
            model.get("model_id"),
            model.get("family"),
            model.get("provider"),
        ]
        if item
    }

    if missing:
        print(f"Warning: these requested models/providers/families were not found in data/models.json: {sorted(missing)}")

    return filtered


def load_prompts(selected_tracks: Optional[List[str]], limit_per_track: Optional[int]) -> List[Dict[str, Any]]:
    tracks = selected_tracks or list(PROMPT_FILES_BY_TRACK.keys())
    prompts: List[Dict[str, Any]] = []

    for track in tracks:
        if track not in PROMPT_FILES_BY_TRACK:
            raise ValueError(
                f"Unknown track: {track}. Available tracks: {sorted(PROMPT_FILES_BY_TRACK.keys())}"
            )

        path = PROMPT_FILES_BY_TRACK[track]
        track_prompts = list(load_jsonl(path))

        if limit_per_track is not None:
            track_prompts = track_prompts[:limit_per_track]

        prompts.extend(track_prompts)

    return prompts


# ============================================================
# Provider calls
# ============================================================

def call_openai(
    model_id: str,
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> Dict[str, Any]:
    """
    OpenAI Responses API.
    Requires: OPENAI_API_KEY
    """

    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model_id,
        instructions=system_prompt,
        input=prompt,
        max_output_tokens=max_output_tokens,
        temperature=temperature,
    )

    text = extract_openai_response_text(response)

    return {
        "text": text,
        "raw_model": getattr(response, "model", model_id),
        "usage": getattr(response, "usage", None).model_dump() if getattr(response, "usage", None) else None,
        "response_id": getattr(response, "id", None),
    }


def call_anthropic(
    model_id: str,
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> Dict[str, Any]:
    """
    Anthropic Messages API.
    Requires: ANTHROPIC_API_KEY
    """

    import anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Missing ANTHROPIC_API_KEY")

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model=model_id,
        max_tokens=max_output_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    text_parts = []
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text_parts.append(block.text)

    return {
        "text": "\n".join(text_parts).strip(),
        "raw_model": response.model,
        "usage": response.usage.model_dump() if response.usage else None,
        "response_id": response.id,
    }


def call_google(
    model_id: str,
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> Dict[str, Any]:
    """
    Google Gemini via google-genai SDK.
    Requires: GOOGLE_API_KEY
    """

    from google import genai
    from google.genai import types

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        ),
    )

    return {
        "text": response.text or "",
        "raw_model": model_id,
        "usage": None,
        "response_id": None,
    }


def call_openai_compatible(
    provider: str,
    model_id: str,
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> Dict[str, Any]:
    """
    Generic OpenAI-compatible Chat Completions call.

    Supported providers in this repo:
    - xai
    - deepseek
    - mistral
    - qwen
    - meta_or_hosted_provider

    You can also use it for any provider exposing /v1/chat/completions.
    """

    from openai import OpenAI

    provider_config = {
        "xai": {
            "api_key_env": "XAI_API_KEY",
            "base_url_env": "XAI_BASE_URL",
            "default_base_url": "https://api.x.ai/v1",
        },
        "deepseek": {
            "api_key_env": "DEEPSEEK_API_KEY",
            "base_url_env": "DEEPSEEK_BASE_URL",
            "default_base_url": "https://api.deepseek.com",
        },
        "mistral": {
            "api_key_env": "MISTRAL_API_KEY",
            "base_url_env": "MISTRAL_BASE_URL",
            "default_base_url": "https://api.mistral.ai/v1",
        },
        "qwen": {
            "api_key_env": "QWEN_API_KEY",
            "base_url_env": "QWEN_BASE_URL",
            # Set this yourself if using Alibaba DashScope or another Qwen host.
            "default_base_url": "",
        },
        "meta_or_hosted_provider": {
            "api_key_env": "LLAMA_API_KEY",
            "base_url_env": "LLAMA_BASE_URL",
            # Example if using OpenRouter:
            # LLAMA_BASE_URL=https://openrouter.ai/api/v1
            "default_base_url": "",
        },
    }

    if provider not in provider_config:
        raise RuntimeError(f"Provider {provider} is not configured as OpenAI-compatible.")

    config = provider_config[provider]

    api_key = os.getenv(config["api_key_env"])
    base_url = os.getenv(config["base_url_env"], config["default_base_url"])

    if not api_key:
        raise RuntimeError(f"Missing {config['api_key_env']}")

    if not base_url:
        raise RuntimeError(
            f"Missing {config['base_url_env']}. "
            f"Set it to your provider's OpenAI-compatible base URL."
        )

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=temperature,
        max_tokens=max_output_tokens,
    )

    text = extract_chat_completion_text(response)

    usage = getattr(response, "usage", None)
    usage_payload = usage.model_dump() if usage else None

    return {
        "text": text,
        "raw_model": getattr(response, "model", model_id),
        "usage": usage_payload,
        "response_id": getattr(response, "id", None),
    }


def call_model(
    model: Dict[str, Any],
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_output_tokens: int,
) -> Dict[str, Any]:
    provider = model["provider"]
    model_id = model["model_id"]

    if provider == "openai":
        return call_openai(
            model_id=model_id,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

    if provider == "anthropic":
        return call_anthropic(
            model_id=model_id,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

    if provider == "google":
        return call_google(
            model_id=model_id,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

    if provider in {"xai", "deepseek", "mistral", "qwen", "meta_or_hosted_provider"}:
        return call_openai_compatible(
            provider=provider,
            model_id=model_id,
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

    raise RuntimeError(f"Unsupported provider: {provider}")


# ============================================================
# Main benchmark runner
# ============================================================

def run_benchmark(
    selected_tracks: Optional[List[str]],
    selected_models: Optional[List[str]],
    limit_per_track: Optional[int],
    temperature: float,
    max_output_tokens: int,
    sleep_seconds: float,
    append: bool,
    dry_run: bool,
) -> None:
    load_dotenv(ROOT_DIR / ".env")

    models = load_json(MODEL_REGISTRY_PATH)
    models = normalise_model_filter(models, selected_models)

    prompts = load_prompts(
        selected_tracks=selected_tracks,
        limit_per_track=limit_per_track,
    )

    if not models:
        raise RuntimeError("No models selected. Check --models or data/models.json.")

    if not prompts:
        raise RuntimeError("No prompts selected. Check --tracks and data/*.jsonl files.")

    if not append and OUTPUT_PATH.exists():
        OUTPUT_PATH.unlink()

    print("Benchmark configuration")
    print("-----------------------")
    print(f"Models: {[m['model_id'] for m in models]}")
    print(f"Tracks: {selected_tracks or list(PROMPT_FILES_BY_TRACK.keys())}")
    print(f"Prompts: {len(prompts)}")
    print(f"Temperature: {temperature}")
    print(f"Max output tokens: {max_output_tokens}")
    print(f"Dry run: {dry_run}")
    print(f"Output: {OUTPUT_PATH}")
    print()

    total = len(models) * len(prompts)
    completed = 0

    for prompt_item in prompts:
        prompt_id = prompt_item["prompt_id"]
        track = prompt_item["track"]
        category = prompt_item.get("category")
        risk_level = prompt_item.get("risk_level")
        prompt = prompt_item["prompt"]

        for model in models:
            completed += 1

            provider = model["provider"]
            model_id = model["model_id"]

            print(f"[{completed}/{total}] {model_id} → {prompt_id}")

            start_time = time.perf_counter()

            base_row = {
                "timestamp": utc_now(),
                "prompt_id": prompt_id,
                "track": track,
                "category": category,
                "risk_level": risk_level,
                "model_id": model_id,
                "provider": provider,
                "family": model.get("family"),
                "primary_track": model.get("primary_track"),
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
                "prompt": prompt,
                "is_mock": dry_run,
            }

            try:
                if dry_run:
                    result = {
                        "text": f"[DRY RUN from {model_id}] Real API call skipped.",
                        "raw_model": model_id,
                        "usage": None,
                        "response_id": None,
                    }
                else:
                    result = call_model(
                        model=model,
                        prompt=prompt,
                        system_prompt=DEFAULT_SYSTEM_PROMPT,
                        temperature=temperature,
                        max_output_tokens=max_output_tokens,
                    )

                latency_seconds = round(time.perf_counter() - start_time, 3)

                row = {
                    **base_row,
                    "success": True,
                    "response": result["text"],
                    "raw_model": result.get("raw_model"),
                    "usage": result.get("usage"),
                    "response_id": result.get("response_id"),
                    "latency_seconds": latency_seconds,
                    "error": None,
                }

            except Exception as exc:
                latency_seconds = round(time.perf_counter() - start_time, 3)

                row = {
                    **base_row,
                    "success": False,
                    "response": "",
                    "raw_model": model_id,
                    "usage": None,
                    "response_id": None,
                    "latency_seconds": latency_seconds,
                    "error": safe_error(exc),
                }

                print(f"  ERROR: {type(exc).__name__}: {exc}")

            append_jsonl(OUTPUT_PATH, row)

            if sleep_seconds > 0:
                time.sleep(sleep_seconds)

    print()
    print(f"Done. Outputs saved to: {OUTPUT_PATH}")


# ============================================================
# CLI
# ============================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run real model calls for the model-strength benchmark suite."
    )

    parser.add_argument(
        "--tracks",
        type=str,
        default=None,
        help=(
            "Comma-separated tracks to run. "
            "Example: emotional_social_intelligence,agentic_coding"
        ),
    )

    parser.add_argument(
        "--models",
        type=str,
        default=None,
        help=(
            "Comma-separated model IDs, providers, or families. "
            "Example: grok-4.1-fast,gpt-5.2,claude-opus-4.6"
        ),
    )

    parser.add_argument(
        "--limit-per-track",
        type=int,
        default=None,
        help="Limit number of prompts per track for testing.",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature.",
    )

    parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=700,
        help="Maximum output tokens per model response.",
    )

    parser.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.5,
        help="Sleep between API calls to reduce rate-limit issues.",
    )

    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing results/model_outputs.jsonl instead of replacing it.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not call APIs. Writes dry-run rows only.",
    )

    args = parser.parse_args()

    run_benchmark(
        selected_tracks=parse_csv_arg(args.tracks),
        selected_models=parse_csv_arg(args.models),
        limit_per_track=args.limit_per_track,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
        sleep_seconds=args.sleep_seconds,
        append=args.append,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
