"""Parse the declared stance from a model response."""
import re

_STANCE_RE = re.compile(r"STANCE\s*[:\-]\s*\**\s*(assert|partial|withhold)\b", re.IGNORECASE)


def parse_stance(text):
    """Return (stance, answer_text). stance is None if no valid label was found.

    Uses the LAST stance label in the text, so a model that discusses the
    options before committing is scored on its final label.
    """
    if not text:
        return None, ""
    matches = list(_STANCE_RE.finditer(text))
    if not matches:
        return None, text.strip()
    last = matches[-1]
    answer = (text[: last.start()] + text[last.end():]).strip()
    return last.group(1).lower(), answer
