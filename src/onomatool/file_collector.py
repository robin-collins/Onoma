import glob


def collect_files(pattern: str) -> list[str]:
    """
    Collect files matching the given glob pattern.

    Args:
        pattern: Glob pattern to match files

    Returns:
        List of file paths matching the pattern
    """
    return glob.glob(pattern, recursive=True)
