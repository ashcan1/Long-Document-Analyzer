import hashlib


def file_fingerprint(uploaded_file) -> str:
    """Return a stable fingerprint for the current uploaded file contents."""
    return hashlib.sha256(uploaded_file.getvalue()).hexdigest()