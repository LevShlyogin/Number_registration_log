def format_doc_no(numeric: int) -> str:
    return f"УТЗ-{str(numeric).zfill(6)}"


def is_golden(numeric: int) -> bool:
    return numeric % 100 == 0