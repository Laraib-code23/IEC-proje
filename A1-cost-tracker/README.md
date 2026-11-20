# A1 Cost Tracker

Run the same prompt against Gemini and Groq, then compare their responses, token
usage, latency, and estimated USD cost. Results are saved to `results.json` in
the current working directory.

## Setup

1. Copy `.env.example` to `.env`.
2. Set your Gemini and Groq API keys and model names.
3. Set each model's current input and output prices in USD per 1 million tokens.
   Prices are not hard-coded because they vary by model and can change.

## Run

```powershell
uv run a1-cost-tracker "Explain how solar panels work"
```

Or run it as a module:

```powershell
uv run python -m a1_cost_tracker "Explain how solar panels work"
```

You can also use the existing script entry point:

```powershell
uv run tracker.py "Explain how solar panels work"
```

API request failures are reported by the provider SDK. Check your API keys,
model names, and account access if a request fails.
