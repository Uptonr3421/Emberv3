from hypothesis import assume


def robust_content_guard(content: str):
    """Skip pathological strings that break embedding/search."""
    assume(len(content.strip()) >= 8)            # >=8 chars
    assume(any(c.isalpha() for c in content))    # must contain letters
    assume(len(set(content)) >= 5)               # >=5 unique chars
    assume(not content[:4].isdigit())            # first 4 not all digits