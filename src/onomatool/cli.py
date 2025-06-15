import argparse
import os
import sys
import tempfile
from pathlib import Path

import toml

from onomatool.config import DEFAULT_CONFIG, get_config
from onomatool.conflict_resolver import resolve_conflict
from onomatool.file_collector import collect_files
from onomatool.file_dispatcher import FileDispatcher
from onomatool.llm_integration import get_suggestions
from onomatool.renamer import rename_file
from onomatool.utils.image_utils import convert_svg_to_png

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    try:
        parser = argparse.ArgumentParser(
            description="Onoma - AI-powered file renaming tool",
            epilog="Configuration is loaded from ~/.onomarc (TOML format)",
            add_help=False,
        )
        parser.add_argument(
            "-h", "--help", action="help", help="Show this help message and exit"
        )
        parser.add_argument(
            "pattern",
            nargs="?",
            help="Glob pattern to match files (e.g., '*.pdf', 'docs/**/*.md')",
        )
        parser.add_argument(
            "-f",
            "--format",
            help="Force specific file format processing (optional)",
            choices=["text", "markdown", "pdf", "docx", "image"],
            metavar="FORMAT",
        )
        parser.add_argument(
            "-s",
            "--save-config",
            action="store_true",
            help="Save default configuration to ~/.onomarc and exit",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            action="store_true",
            help="Print LLM request and response for debugging",
        )
        parser.add_argument(
            "-d",
            "--dry-run",
            action="store_true",
            help="Show intended renames but do not modify any files",
        )
        parser.add_argument(
            "-i",
            "--interactive",
            action="store_true",
            help=(
                "With --dry-run, prompt for confirmation and then perform the renames "
                "using the dry-run suggestions"
            ),
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help=(
                "Do not delete temporary files created for SVG, PDF, or PPTX processing; "
                "print their paths."
            ),
        )
        args = parser.parse_args()

        if args.save_config:
            save_default_config()
            print("Default configuration saved to ~/.onomarc")
            return

        if not args.pattern:
            parser.error("the following arguments are required: pattern")

        if args.interactive and not args.dry_run:
            parser.error("--interactive must be used with --dry-run")

        get_config()
        files = collect_files(args.pattern)
        dispatcher = FileDispatcher(debug=args.debug)

        planned_renames = []

        for file_path in files:
            if args.debug:
                print(f"[DEBUG] Processing file: {file_path}")
            _, ext = os.path.splitext(file_path)
            is_svg = ext.lower() == ".svg"
            tempdir = None
            png_path = None
            if is_svg:
                tempdir = tempfile.TemporaryDirectory()
                print(
                    f"[DEBUG] Created tempdir for SVG: {tempdir.name}"
                ) if args.debug else None
                try:
                    png_path = convert_svg_to_png(file_path, tempdir.name)
                    if args.debug:
                        print(f"[DEBUG] Created PNG: {png_path}")
                except Exception as e:
                    print(f"[SVG ERROR] Could not convert {file_path} to PNG: {e}")
                    if tempdir is not None and not args.debug:
                        tempdir.cleanup()
                    continue
            result = dispatcher.process(file_path)
            if not result:
                if tempdir is not None and not args.debug:
                    tempdir.cleanup()
                continue
            try:
                if is_svg and png_path:
                    # Always use PNG for all LLM input for SVGs
                    all_image_suggestions = []
                    img_suggestions = get_suggestions(
                        "", verbose=args.verbose, file_path=png_path
                    )
                    if img_suggestions:
                        all_image_suggestions.append(img_suggestions)
                    flat_image_suggestions = [
                        s for sublist in all_image_suggestions for s in sublist
                    ]
                    md_suggestions = get_suggestions(
                        result
                        if isinstance(result, str)
                        else result.get("markdown", ""),
                        verbose=args.verbose,
                        file_path=png_path,
                    )
                    guidance = "\n".join(flat_image_suggestions)
                    final_prompt = (
                        "You have previously suggested the following file names for each "
                        "page/slide/image of the file:\n"
                        f"{guidance}\n"
                        "Now, based on the full document content (markdown below) and the "
                        "above suggestions, generate 3 final file name suggestions that best "
                        "represent the entire file.\n"
                        f"MARKDOWN:\n{result if isinstance(result, str) else result.get('markdown', '')}"
                    )
                    final_suggestions = get_suggestions(
                        final_prompt, verbose=args.verbose, file_path=png_path
                    )
                    suggestions = (
                        final_suggestions or md_suggestions or flat_image_suggestions
                    )
                    if suggestions:
                        new_name = suggestions[0]
                        directory = os.path.dirname(file_path) or "."
                        base_new_name, _ = os.path.splitext(new_name)
                        new_name_with_ext = base_new_name + ext
                        existing_files = os.listdir(directory)
                        final_name = resolve_conflict(new_name_with_ext, existing_files)
                        if args.dry_run:
                            print(f"{os.path.basename(file_path)} --> {final_name}")
                            planned_renames.append((file_path, new_name))
                        else:
                            rename_file(file_path, new_name)
                else:
                    # Non-SVG logic unchanged
                    if (
                        isinstance(result, dict)
                        and "markdown" in result
                        and "images" in result
                    ):
                        images = result["images"]
                        tempdir = result.get("tempdir")
                        if tempdir is not None and args.debug:
                            print(
                                f"[DEBUG] Created tempdir for PDF/PPTX: {tempdir.name}"
                            )
                            for img_path in images:
                                print(f"[DEBUG] Created image: {img_path}")
                        all_image_suggestions = []
                        for img_path in images:
                            img_suggestions = get_suggestions(
                                "", verbose=args.verbose, file_path=img_path
                            )
                            if img_suggestions:
                                all_image_suggestions.append(img_suggestions)
                        flat_image_suggestions = [
                            s for sublist in all_image_suggestions for s in sublist
                        ]
                        md_file_path = images[0] if len(images) > 0 else file_path
                        md_suggestions = get_suggestions(
                            result["markdown"],
                            verbose=args.verbose,
                            file_path=md_file_path,
                        )
                        guidance = "\n".join(flat_image_suggestions)
                        final_prompt = (
                            "You have previously suggested the following file names for each "
                            "page/slide/image of the file:\n"
                            f"{guidance}\n"
                            "Now, based on the full document content (markdown below) and the "
                            "above suggestions, generate 3 final file name suggestions that best "
                            "represent the entire file.\n"
                            f"MARKDOWN:\n{result['markdown']}"
                        )
                        final_suggestions = get_suggestions(
                            final_prompt, verbose=args.verbose, file_path=md_file_path
                        )
                        suggestions = (
                            final_suggestions
                            or md_suggestions
                            or flat_image_suggestions
                        )
                        if suggestions:
                            new_name = suggestions[0]
                            directory = os.path.dirname(file_path) or "."
                            _, ext = os.path.splitext(file_path)
                            base_new_name, _ = os.path.splitext(new_name)
                            new_name_with_ext = base_new_name + ext
                            existing_files = os.listdir(directory)
                            final_name = resolve_conflict(
                                new_name_with_ext, existing_files
                            )
                            if args.dry_run:
                                print(f"{os.path.basename(file_path)} --> {final_name}")
                                planned_renames.append((file_path, new_name))
                            else:
                                rename_file(file_path, new_name)
                    else:
                        content = result
                        suggestions = get_suggestions(
                            content, verbose=args.verbose, file_path=file_path
                        )
                        if suggestions:
                            new_name = suggestions[0]  # Use first suggestion in Phase 1
                            directory = os.path.dirname(file_path) or "."
                            _, ext = os.path.splitext(file_path)
                            base_new_name, _ = os.path.splitext(new_name)
                            new_name_with_ext = base_new_name + ext
                            existing_files = os.listdir(directory)
                            final_name = resolve_conflict(
                                new_name_with_ext, existing_files
                            )
                            if args.dry_run:
                                print(f"{os.path.basename(file_path)} --> {final_name}")
                                planned_renames.append((file_path, new_name))
                            else:
                                rename_file(file_path, new_name)
            finally:
                if tempdir is not None and not args.debug:
                    tempdir.cleanup()

        if args.dry_run and args.interactive and planned_renames:
            confirm = input("\nProceed with these renames? [y/N]: ").strip().lower()
            if confirm == "y":
                for file_path, new_name in planned_renames:
                    rename_file(file_path, new_name)
            else:
                print("Aborted. No files were renamed.")
    except KeyboardInterrupt:
        print("\nOperation cancelled by user (Ctrl+C). Exiting gracefully.")
        sys.exit(130)
    except SystemExit:
        # Allow normal sys.exit() and argparse exits without stack trace
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def save_default_config():
    """Save default configuration to ~/.onomarc"""
    config_path = os.path.expanduser("~/.onomarc")
    # Ensure llm_model is in the main section and not in markitdown
    config = DEFAULT_CONFIG.copy()
    if "markitdown" in config and "llm_model" in config["markitdown"]:
        del config["markitdown"]["llm_model"]
    config["llm_model"] = config.get("llm_model", "gpt-4o")
    config["image_prompt"] = config.get("image_prompt", "")
    try:
        with open(config_path, "w") as f:
            toml.dump(config, f)
    except Exception as e:
        print(f"Error saving default config: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
