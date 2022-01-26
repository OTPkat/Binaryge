def is_positive_binary_string(s: str):
    return all(x in '01' for x in s) and any(x == 1 for x in s)
