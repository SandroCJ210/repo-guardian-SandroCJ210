import textdistance

def is_rewrite(path_a: list[str], path_b: list[str], threshold: float = 0.92) -> bool:
    if not path_a or not path_b:
        return False

    str_a = "→".join(path_a)
    str_b = "→".join(path_b)
    similarity = textdistance.jaro_winkler.normalized_similarity(str_a, str_b)
    return similarity >= threshold
