import os
import shutil

from .conflict_resolver import resolve_conflict


def rename_file(original_path: str, new_name: str) -> None:
    """
    Rename a file, resolving conflicts using numeric suffixes.
    Always preserve the original file extension.

    Args:
        original_path: Path to the original file
        new_name: Desired new base name for the file (extension will be preserved)
    """
    directory = os.path.dirname(original_path) or "."
    # Always preserve the original file extension
    _, ext = os.path.splitext(original_path)
    base_new_name, _ = os.path.splitext(new_name)
    new_name_with_ext = base_new_name + ext
    os.path.join(directory, new_name_with_ext)

    # Get list of existing files in the directory
    existing_files = os.listdir(directory)

    # Resolve conflict if needed
    final_name = resolve_conflict(new_name_with_ext, existing_files)
    final_path = os.path.join(directory, final_name)

    # Perform the rename
    shutil.move(original_path, final_path)
    print(f"Renamed '{os.path.basename(original_path)}' to '{final_name}'")
