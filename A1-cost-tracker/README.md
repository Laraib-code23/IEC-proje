# A1 Cost Tracker

Sends the same prompt to Gemini and Groq, then shows each reply, the token
counts, the time and the cost in USD. It also saves `results.json`.

## Setup

1. `uv sync`
2. Copy  and add your own keys and model names.
3. Prices (USD per 1M tokens) are set at the top of `tracker.py`.

## Run

```powershell
uv run tracker.py "What is the capital of Germany."
```

## Sample output

```
----------------------------------------------------------
provider     input  output   seconds      cost_usd
----------------------------------------------------------
gemini        8     80      70.46          0.000612
groq           78      49     0.85           0.000021
----------------------------------------------------------
```

## What I learned

I learned that different models work differently on the same prompt, and that the price depends on the number of tokens. After learning this, I asked myself if the free version is charged. I found that the free tier costs nothing but has limits, and the cost in my table is what the call would cost on the paid tier.
