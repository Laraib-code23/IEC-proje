import os
import sys

from google import genai
from google.genai import types
from pydantic import ValidationError

from schema import Extracted

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "extract.txt")
MAX_ATTEMPTS = 3
DEFAULT_MODEL = "gemini-3.6-flash"


class ExtractionError(Exception):
    """Raised when extraction fails after all attempts."""


def load_dotenv() -> None:
    """Load simple KEY=VALUE entries from the project's .env without dependencies."""
    env_path = os.path.join(BASE_DIR, ".env")
    try:
        with open(env_path, encoding="utf-8") as env_file:
            for line in env_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[7:].lstrip()
                key, separator, value = line.partition("=")
                if not separator or not key.strip():
                    continue
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                    value = value[1:-1]
                os.environ.setdefault(key.strip(), value)
    except FileNotFoundError:
        pass


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def get_model() -> str:
    # Set GEMINI_MODEL in .env to change the model without editing code.
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def read_prompt() -> str:
    try:
        with open(PROMPT_PATH, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise ExtractionError(f"Missing prompt file at {PROMPT_PATH}")


def make_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ExtractionError("GEMINI_API_KEY is missing. Put it in .env")
    return genai.Client(api_key=api_key)


def ask(client, system_prompt: str, text: str, logger=log) -> Extracted:
    """Call Gemini with structured output, validate, retry with the error."""
    model = get_model()
    contents = [
        types.Content(role="user", parts=[types.Part(text=f"<text>\n{text}\n</text>")])
    ]
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        logger(f"attempt {attempt}/{MAX_ATTEMPTS} (model: {model})")
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_schema=Extracted,
                    temperature=0,
                ),
            )
            reply = response.text or ""
        except Exception as e:  # API/network error
            last_error = f"API error: {e}"
            logger(last_error)
            continue

        try:
            return Extracted.model_validate_json(reply)
        except ValidationError as e:
            last_error = str(e)
            logger(f"validation failed: {last_error}")
            # Send the reply AND the error back so the model can fix it.
            contents.append(types.Content(role="model", parts=[types.Part(text=reply)]))
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text="Your JSON failed validation with this error:\n"
                            f"{last_error}\nReturn corrected JSON only."
                        )
                    ],
                )
            )
    raise ExtractionError(f"Failed after {MAX_ATTEMPTS} attempts. Last error: {last_error}")


def main() -> None:
    load_dotenv()
    if len(sys.argv) < 2:
        log('Usage: uv run extract.py "your messy text here"')
        sys.exit(2)
    text = sys.argv[1]
    try:
        client = make_client()
        result = ask(client, read_prompt(), text)
    except ExtractionError as e:
        log(f"Error: {e}")
        sys.exit(1)
    print(result.model_dump_json(indent=2))  # the ONLY thing on stdout


if __name__ == "__main__":
    main()
