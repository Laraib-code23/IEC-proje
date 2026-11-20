import argparse
import json
import math
import os
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv


@dataclass(frozen=True)
class ProviderConfig:
    api_key: str
    model: str
    input_price_per_m: float
    output_price_per_m: float


def _read_config() -> tuple[ProviderConfig, ProviderConfig]:
    names = (
        "GEMINI_API_KEY",
        "GEMINI_MODEL",
        "GEMINI_INPUT_PRICE_PER_M",
        "GEMINI_OUTPUT_PRICE_PER_M",
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "GROQ_INPUT_PRICE_PER_M",
        "GROQ_OUTPUT_PRICE_PER_M",
    )
    missing = [name for name in names if not os.getenv(name, "").strip()]
    if missing:
        raise ValueError(
            "Missing .env values: "
            + ", ".join(missing)
            + ". Copy .env.example to .env and fill in each value."
        )

    def provider_config(provider: str) -> ProviderConfig:
        input_price = float(os.environ[f"{provider}_INPUT_PRICE_PER_M"])
        output_price = float(os.environ[f"{provider}_OUTPUT_PRICE_PER_M"])
        if (
            not math.isfinite(input_price)
            or not math.isfinite(output_price)
            or input_price < 0
            or output_price < 0
        ):
            raise ValueError(f"{provider} token prices must be finite and non-negative.")
        return ProviderConfig(
            api_key=os.environ[f"{provider}_API_KEY"],
            model=os.environ[f"{provider}_MODEL"],
            input_price_per_m=input_price,
            output_price_per_m=output_price,
        )

    return provider_config("GEMINI"), provider_config("GROQ")


def _call_gemini(prompt: str, config: ProviderConfig) -> tuple[str | None, int, int]:
    from google import genai

    client = genai.Client(api_key=config.api_key)
    response = client.models.generate_content(model=config.model, contents=prompt)
    usage = response.usage_metadata
    if usage is None or usage.prompt_token_count is None:
        raise RuntimeError("Gemini response did not include token usage.")
    output_tokens = (usage.candidates_token_count or 0) + (
        usage.thoughts_token_count or 0
    )
    return response.text, usage.prompt_token_count, output_tokens


def _call_groq(prompt: str, config: ProviderConfig) -> tuple[str | None, int, int]:
    from groq import Groq

    client = Groq(api_key=config.api_key)
    response = client.chat.completions.create(
        model=config.model,
        messages=[{"role": "user", "content": prompt}],
    )
    usage = response.usage
    if usage is None:
        raise RuntimeError("Groq response did not include token usage.")
    reply = response.choices[0].message.content
    return reply, usage.prompt_tokens, usage.completion_tokens


def _run_provider(
    provider: str,
    config: ProviderConfig,
    call: Callable[[str, ProviderConfig], tuple[str | None, int, int]],
    prompt: str,
) -> tuple[dict[str, Any], float]:
    started = time.perf_counter()
    reply, input_tokens, output_tokens = call(prompt, config)
    seconds = time.perf_counter() - started
    cost_usd = (
        input_tokens * config.input_price_per_m
        + output_tokens * config.output_price_per_m
    ) / 1_000_000
    return (
        {
            "provider": provider,
            "model": config.model,
            "reply": reply,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_price_per_m": config.input_price_per_m,
            "output_price_per_m": config.output_price_per_m,
            "cost_usd": cost_usd,
        },
        seconds,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare Gemini and Groq responses, token usage, latency, and cost."
    )
    parser.add_argument("prompt", nargs="+", help="Prompt to send to both providers.")
    args = parser.parse_args(argv)

    load_dotenv()
    try:
        gemini_config, groq_config = _read_config()
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2

    prompt = " ".join(args.prompt)
    results = [
        _run_provider("gemini", gemini_config, _call_gemini, prompt),
        _run_provider("groq", groq_config, _call_groq, prompt),
    ]

    for result, _ in results:
        print(f"\n=== {result['provider']} ({result['model']}) ===")
        print(result["reply"] or "")

    print("\n" + "-" * 58)
    print(f"{'provider':<10}{'input':>8}{'output':>8}{'seconds':>10}{'cost_usd':>14}")
    print("-" * 58)
    for result, seconds in results:
        print(
            f"{result['provider']:<10}{result['input_tokens']:>8}"
            f"{result['output_tokens']:>8}{seconds:>10.2f}"
            f"{result['cost_usd']:>14.6f}"
        )
    print("-" * 58)

    with open("results.json", "w", encoding="utf-8") as results_file:
        json.dump([result for result, _ in results], results_file, indent=2)
    print("Saved results.json")
    return 0
