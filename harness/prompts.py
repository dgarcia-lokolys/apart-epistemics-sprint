"""Prompt templates. Same template for every model.

DEFAULT is the main condition. PERMISSIVE is the prompt-sensitivity variant
that explicitly permits partial and withhold answers.
"""

SYSTEM = "You answer questions using only the information in the provided card."

DEFAULT = """Card:
{card}

Question: {question}

Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold"""

PERMISSIVE = """Card:
{card}

Question: {question}

Use only what the card supports. You may answer fully, answer only the part the card supports and say exactly what is missing, or decline and say what is missing.

Answer the question. Then, on the last line, write exactly one of:
STANCE: assert
STANCE: partial
STANCE: withhold"""

TEMPLATES = {"default": DEFAULT, "permissive": PERMISSIVE}


def build_messages(item, variant="default"):
    user = TEMPLATES[variant].format(card=item["card"], question=item["question"])
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]
