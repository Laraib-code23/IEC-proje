import json
import os
import sys
import time

from dotenv import load_dotenv
from google import genai
from groq import Groq

# 1. .env se keys aur model names load karo
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL")
GROQ_MODEL = os.getenv("GROQ_MODEL")

# 2. Prices: USD per 1 MILLION tokens
#    TODO: pricing pages se dekh kar bharo
GEMINI_INPUT_PRICE_PER_M = 1.50
GEMINI_OUTPUT_PRICE_PER_M = 7.50
GROQ_INPUT_PRICE_PER_M = 0.075
GROQ_OUTPUT_PRICE_PER_M = 0.30


# 3. Check: prompt, keys aur models maujood hain ya nahi
def check_setup():
    if len(sys.argv) < 2:
        print('Usage: uv run tracker.py "your prompt"')
        sys.exit(1)

    required = ["GEMINI_API_KEY", "GROQ_API_KEY", "GEMINI_MODEL", "GROQ_MODEL"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        print("Missing in .env: " + ", ".join(missing))
        print("Copy .env.example to .env and fill in the values.")
        sys.exit(1)


# 4. Har provider ka function: (reply, input_tokens, output_tokens)
def call_gemini(prompt):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
    usage = response.usage_metadata
    input_tokens = usage.prompt_token_count
    output_tokens = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
    return response.text, input_tokens, output_tokens


def call_groq(prompt):
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    reply = response.choices[0].message.content
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    return reply, input_tokens, output_tokens


# 5. Call chalao, time naapo, cost nikalo
def run_provider(provider, model, call_function, prompt, input_price, output_price):
    start = time.time()
    try:
        reply, input_tokens, output_tokens = call_function(prompt)
    except Exception as error:
        print(f"{provider} call failed: {error}")
        sys.exit(1)
    seconds = time.time() - start

    cost_usd = (
        input_tokens * input_price / 1_000_000
        + output_tokens * output_price / 1_000_000
    )

    result = {
        "provider": provider,
        "model": model,
        "reply": reply,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "input_price_per_m": input_price,
        "output_price_per_m": output_price,
        "cost_usd": cost_usd,
    }
    return result, seconds


# 6. Main: dono chalao, print karo, json save karo
def main():
    check_setup()
    prompt = sys.argv[1]

    gemini_result, gemini_seconds = run_provider(
        "gemini", GEMINI_MODEL, call_gemini, prompt,
        GEMINI_INPUT_PRICE_PER_M, GEMINI_OUTPUT_PRICE_PER_M,
    )
    groq_result, groq_seconds = run_provider(
        "groq", GROQ_MODEL, call_groq, prompt,
        GROQ_INPUT_PRICE_PER_M, GROQ_OUTPUT_PRICE_PER_M,
    )

    results = [gemini_result, groq_result]
    timings = [gemini_seconds, groq_seconds]

    for r in results:
        print(f"\n=== {r['provider']} ({r['model']}) ===")
        print(r["reply"])

    print("\n" + "-" * 58)
    print(f"{'provider':<10}{'input':>8}{'output':>8}{'seconds':>10}{'cost_usd':>14}")
    print("-" * 58)
    for r, secs in zip(results, timings):
        print(
            f"{r['provider']:<10}{r['input_tokens']:>8}{r['output_tokens']:>8}"
            f"{secs:>10.2f}{r['cost_usd']:>14.6f}"
        )
    print("-" * 58)

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("Saved results.json")


if __name__ == "__main__":
    main()