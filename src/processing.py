import tiktoken
from openai import OpenAI
from pydantic import ValidationError
from src.models import AnalysisResult

# The encoding for GPT-4o — tells tiktoken how to split text into tokens
ENCODING = tiktoken.encoding_for_model("gpt-4o")

# GPT-4o context window limit (input)
MAX_TOKENS = 128_000

# GPT-4o maximum response size (output)
MAX_OUTPUT_TOKENS = 16_384

# Safe chunk size — leave room for the model's response
CHUNK_SIZE = MAX_TOKENS - MAX_OUTPUT_TOKENS  # 111,616 tokens per chunk


def count_tokens(text: str) -> int:
    """Returns the number of tokens in the text."""
    return len(ENCODING.encode(text))


def fits_in_context(text: str) -> bool:
    """Returns True if the text fits in one GPT-4o request."""
    return count_tokens(text) <= MAX_TOKENS


def chunk_text(text: str) -> list[str]:
    """Split text into chunks that each fit within CHUNK_SIZE tokens.

    Splits by paragraph so chunks don't cut in the middle of a sentence.
    Each chunk keeps adding paragraphs until the next one would exceed
    CHUNK_SIZE — then it starts a new chunk.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        candidate = current_chunk + "\n\n" + paragraph if current_chunk else paragraph
        if count_tokens(candidate) > CHUNK_SIZE:
            # Current chunk is full — save it and start a new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk = candidate

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def extract_text(file) -> str:
    return file.getvalue().decode("utf-8")


def clean_text(text: str) -> str:
    if text is None or not text.strip():
        return ""

    cleaned_lines = []
    previous_line_was_blank = True

    for line in text.splitlines():
        cleaned_line = line.strip()
        if not cleaned_line:
            if not previous_line_was_blank:
                cleaned_lines.append("")
            previous_line_was_blank = True
            continue
        cleaned_lines.append(cleaned_line)
        previous_line_was_blank = False

    return "\n".join(cleaned_lines).strip()


def analyze(text: str) -> AnalysisResult:
    prompt = (
        "Analyze the document below and extract a summary, the key points, "
        f"and your confidence in the analysis.\n\nDocument:\n{text}"
    )

    # Reads the API key from the OPENAI_API_KEY environment variable
    client = OpenAI()
    response = client.chat.completions.parse(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,  # low = consistent, repeatable summaries, not creative ones
        response_format=AnalysisResult,  # Structured Outputs — reply is guaranteed to match this schema
    )

    # .parsed is already a validated AnalysisResult instance
    return response.choices[0].message.parsed


def result_to_dict(result: AnalysisResult) -> dict:
    return result.model_dump()


def result_to_json(result: AnalysisResult) -> str:
    return result.model_dump_json(indent=2)
