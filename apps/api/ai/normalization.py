import re


def clean_header(header: str) -> str:
    cleaned = header.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned
