import re

def generate_slug_from_title(title: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', title).lower()

    # if there's a leading dash, remove it``
    if slug[0] == '-':
        slug = slug[1:]

    # if there's a trailing dash, remove it
    if slug[-1] == '-':
        slug = slug[:-1]

    return slug