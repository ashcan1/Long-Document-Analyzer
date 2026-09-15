"""Document processing logic kept separate from the Streamlit user interface."""


def extract_text(file) -> str:
    """Convert an uploaded text file from bytes into a Python string.

    Streamlit gives us the uploaded file object. Its ``getvalue`` method
    returns bytes, so ``decode`` converts those bytes into readable text.
    """
    return file.getvalue().decode("utf-8")


def clean_text(text: str) -> str:
    """Clean formatting while preserving the document's words.

    The function processes one line at a time so it can remove extra spaces
    and keep paragraph breaks. It allows one blank line between paragraphs,
    but removes blank lines at the beginning and end of the document.
    """
    if text is None or not text.strip():
        return ""

    cleaned_lines = []

    # This prevents several consecutive blank lines from being copied.
    previous_line_was_blank = True

    # splitlines handles common Windows, Linux, and macOS line endings.
    for line in text.splitlines():
        # strip removes spaces and tabs around the line, not inside words.
        cleaned_line = line.strip()
        if not cleaned_line:
            # Keep only the first blank line after real content.
            if not previous_line_was_blank:
                cleaned_lines.append("")
            previous_line_was_blank = True
            continue

        # Keep non-empty lines in their original order.
        cleaned_lines.append(cleaned_line)
        previous_line_was_blank = False

    # Join the cleaned lines and remove outer blank space.
    return "\n".join(cleaned_lines).strip()




def analyze(text: str) -> dict:
    """Reserve the future analysis step for summaries and questions."""
    raise NotImplementedError
