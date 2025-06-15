import os


def resolve_conflict(desired_name: str, existing_names: list[str]) -> str:
    """
    Resolve naming conflicts by appending a numeric suffix.

    Args:
        desired_name: The desired base name for the file
        existing_names: List of existing file names in the target directory

    Returns:
        A unique file name by appending a numeric suffix if needed
    """
    if desired_name not in existing_names:
        return desired_name

    base, ext = os.path.splitext(desired_name)
    counter = 2
    while True:
        new_name = f"{base}_{counter}{ext}"
        if new_name not in existing_names:
            return new_name
        counter += 1
