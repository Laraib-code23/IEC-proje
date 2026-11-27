Messy text to JSON (Assignment 2)

Turns messy job posts into clean JSON using Gemini structured output + Pydantic.

Setup
bash
uv sync
cp .env.example .env   # then put your GEMINI_API_KEY in .env
Run
bash
uv run extract.py "We're hiring a Python dev at Acme, Lahore. 3+ years, Django. PKR 300k/month"

Only JSON goes to stdout. Logs and errors go to stderr.

Files
extract.py : CLI + ask() with retries
schema.py : the Extracted Pydantic model (all fields Optional except is_job_post)
prompts/extract.txt : the prompt (not inside the code)
samples/ and outputs/ : 5 samples + 4 edge cases and their saved results
How retries work

Gemini is asked for JSON matching Extracted. If Pydantic validation fails, the bad reply and the validation error are sent back to the model. Max 3 attempts, then exit code 1 with a clear message on stderr.

Edge cases
Input	Result
Empty text	is_job_post: false, all null
Urdu job post	extracted normally
Junk text	is_job_post: false
Prompt injection	treated as data, job extracted, instruction ignored

(Fill in what your real outputs show.)

Notes
API key is only in .env (git-ignored). Never committed.