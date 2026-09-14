"""Document parsing and analysis logic, independent of the Streamlit UI."""


def extract_text(file) -> str:
    """Read the contents of an uploaded text file."""
    return file.getvalue().decode("utf-8")


def analyze(text: str) -> dict:
    raise NotImplementedError
