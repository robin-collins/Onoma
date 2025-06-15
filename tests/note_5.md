# Feature Proposal: Add --debug Flag to CLI

**Date:** 2024-06-14
**Proposer:** Alice

## Motivation
- Users and developers need better visibility into temporary file handling and processing steps, especially for complex file conversions (SVG, PDF, PPTX).
- Debugging issues with file conversion, renaming, and LLM input is difficult without access to temp files and detailed logs.
- Current CLI output does not provide enough information for troubleshooting failed conversions or unexpected results.
- Support requests and bug reports often require users to manually reproduce issues with additional logging enabled.

## Requirements
- Add a `--debug` flag to the CLI, documented in the help output and user guide.
- When enabled, do not delete temporary files or directories created during file processing (e.g., SVG-to-PNG, PDF-to-image, PPTX-to-image conversions).
- Print the full path of all temp files and directories to the console, with clear `[DEBUG]` markers.
- Ensure debug output is clear, concise, and easy to find in logs.
- Debug mode should be compatible with all CLI options, including dry-run and interactive modes.
- No temp files should be left behind when `--debug` is not set.
- All debug output should be routed to stdout for easy capture in CI and user bug reports.

## Design
- Update CLI argument parser in `cli.py` to include `--debug` (boolean flag).
- Pass debug flag to all file processing and dispatcher modules (`file_dispatcher.py`, `processors/markitdown_processor.py`).
- In debug mode, print `[DEBUG]` messages for temp file creation, conversion steps, and cleanup decisions.
- Refactor temp file management utilities to accept a debug flag and conditionally skip cleanup.
- Ensure all temp file creation and deletion is logged in debug mode, including errors and exceptions.
- Add debug output for LLM request/response if `--verbose` is also set.

## Technical Implementation
- Modify `main()` in `cli.py` to parse and propagate the debug flag.
- Update `FileDispatcher` and `MarkitdownProcessor` to accept and use the debug flag.
- Refactor temp file utilities in `utils/image_utils.py` to support debug mode.
- Add debug logging to all conversion steps (SVG-to-PNG, PDF-to-image, PPTX-to-image).
- Ensure that temp directories are only cleaned up if debug is not enabled.
- Add tests in `tests/test_usage_enduser.py` to verify debug output and temp file persistence.

## User Stories
- As a developer, I want to see the full path of temp files created during file processing so I can debug conversion issues.
- As a user, I want to enable debug mode when reporting bugs so I can provide detailed logs to the support team.
- As a tester, I want to verify that temp files are not deleted in debug mode and are cleaned up otherwise.

## Acceptance Criteria
- [ ] When `--debug` is set, temp files are not deleted and their paths are printed with `[DEBUG]` markers.
- [ ] When `--debug` is not set, temp files are cleaned up as before.
- [ ] Debug output includes clear `[DEBUG]` markers and is routed to stdout.
- [ ] Feature is covered by automated tests in `tests/test_usage_enduser.py`.
- [ ] Documentation and help output are updated to describe the `--debug` flag.

## Risks and Mitigation
- **Risk:** Users may forget to clean up temp files after running in debug mode.
  - *Mitigation:* Print a summary of temp files at the end of processing and provide a cleanup command in the docs.
- **Risk:** Debug output may clutter logs or overwhelm users.
  - *Mitigation:* Use clear `[DEBUG]` markers and group debug output at the end of processing where possible.
- **Risk:** Inconsistent debug behavior across modules.
  - *Mitigation:* Standardize debug flag handling and logging format in all modules.
- **Risk:** Temp files may consume excessive disk space in long debug sessions.
  - *Mitigation:* Warn users if temp directory exceeds a threshold size in debug mode.

## Related Modules
- `src/onomatool/cli.py` (argument parsing, main logic)
- `src/onomatool/file_dispatcher.py` (file dispatch and processing)
- `src/onomatool/processors/markitdown_processor.py` (PDF/PPTX/image handling)
- `src/onomatool/utils/image_utils.py` (SVG/PDF conversion utilities)
- `tests/test_usage_enduser.py` (test coverage for debug mode)

## Test Strategy
- Add tests to verify that temp files are not deleted in debug mode and are cleaned up otherwise.
- Capture and assert on debug output in CLI tests.
- Test all file types (markdown, image, PDF, SVG, PPTX) in debug mode.
- Simulate errors in conversion steps and verify debug output includes error details.

## Notes
- This feature will improve troubleshooting and support for end users and developers.
- Will coordinate with QA (Carol) and DevOps (Frank) to ensure debug output is useful in CI and bug reports.
