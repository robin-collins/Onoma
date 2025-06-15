# User Feedback Summary

**Date:** 2024-06-13
**User:** Carol (beta tester)

## Feedback Points
- The CLI is easy to use but could benefit from more detailed help output, including real-world usage examples and troubleshooting tips.
- Users want to specify custom file naming conventions beyond the built-in options (snake_case, camelCase, PascalCase, etc.).
- Output formats for renamed files should be configurable, allowing users to define templates (e.g., `{date}_{name}.{ext}`) in the config file.
- The dry-run mode is helpful, but an option to export planned renames to a file (CSV or JSON) would be useful for review and audit purposes.
- More examples in the documentation would help new users, especially for advanced features like batch processing and recursive directory traversal.
- Error messages should be more descriptive, especially for file permission issues, invalid config files, and unsupported file types.
- Interactive mode should allow reviewing all planned renames before confirmation, with a summary table and the ability to skip or edit individual renames.
- The `--debug` flag is valuable, but users would like a summary of all temp files created and guidance on cleanup.
- Some users reported confusion about how to override the default config and where to place custom config files.
- Requests for a `--help-examples` flag to show usage scenarios and best practices.
- Users want to see a preview of the new file names before confirming changes, especially in batch mode.
- Some users encountered issues with non-UTF-8 files and would like better support and error handling for these cases.
- Feedback on the mock provider was positive; users appreciated the ability to run tests and demos without real LLM API calls.
- Suggestions to add a GUI or web interface for non-CLI users in the future.
- Users would like to see a summary of all actions taken at the end of a run, including skipped files and errors.
- Some users requested color-coded output for better readability in terminals.
- Users want the ability to undo the last batch of renames in case of mistakes.
- Requests for integration with file explorers (e.g., right-click rename with Onoma) for Windows and Linux.
- Users want to be able to specify exclusion patterns (e.g., skip hidden files or certain extensions).
- Some users suggested adding a `--version` flag to quickly check the installed version.

## Suggestions
- Add a `--help-examples` flag to show usage examples and advanced scenarios.
- Allow users to define custom naming patterns and output templates in the config file.
- Support exporting dry-run results to a file (CSV, JSON, or Markdown).
- Expand documentation with real-world scenarios, troubleshooting tips, and a FAQ section.
- Improve error handling and provide actionable suggestions in error messages.
- Enhance interactive mode to display a summary table and allow editing/skipping planned renames.
- Provide a summary of temp files created in debug mode and add a cleanup command to the docs.
- Clarify config override behavior in the documentation and provide examples for different environments.
- Add support for non-UTF-8 files and document limitations or workarounds.
- Consider adding a GUI or web dashboard for broader accessibility.
- Add a `--version` flag and color-coded output for better UX.
- Implement an undo feature for batch renames.
- Support exclusion patterns in CLI and config.
- Integrate with file explorers for right-click renaming.

## Specific Examples
- User ran: `onoma tests/*.md --dry-run --interactive` and wanted to export the planned renames to `planned_renames.csv`.
- User tried: `onoma tests/note_0.md --config custom.toml` but was unsure if the config was loaded; suggested adding a confirmation message.
- User encountered: `UnicodeDecodeError` on a binary file and requested a clearer error message and skip option.
- User wanted to preview all renames in a table before confirming in interactive mode.
- User ran: `onoma --version` and expected to see the installed version.
- User used: `onoma --help-examples` and wanted to see advanced usage scenarios.
- User requested: `onoma --exclude '*.tmp'` to skip temporary files during batch renaming.

## Follow-up Actions
- [ ] Review and prioritize feedback with the team at the next sprint planning meeting.
- [ ] Draft design proposals for custom naming and output formats.
- [ ] Update documentation with more examples, troubleshooting tips, and a FAQ.
- [ ] Plan usability testing for the next release, focusing on new features and error handling.
- [ ] Add a section to the docs on config overrides and environment-specific setups.
- [ ] Prototype export functionality for dry-run results.
- [ ] Investigate color-coded output and undo feature feasibility.
- [ ] Explore integration options with file explorers.

## Impact Assessment
- Improved help output and documentation will lower the barrier for new users and reduce support requests.
- Custom naming and output templates will make the tool more flexible for diverse workflows.
- Export and preview features will increase user confidence and support audit/compliance needs.
- Better error handling and debug summaries will streamline troubleshooting and bug reporting.
- Support for non-UTF-8 files and clear config override guidance will improve reliability in enterprise environments.
- Color-coded output and undo features will enhance user experience and safety.
- Integration with file explorers will broaden the tool's reach to non-CLI users.

## Future Roadmap
- Q3: Implement custom naming templates, export functionality, and enhanced interactive mode.
- Q3: Add `--help-examples`, `--version`, and color-coded output.
- Q4: Expand documentation, add FAQ, and improve error handling for edge cases.
- Q4: Begin prototyping GUI/web interface and file explorer integration for broader accessibility.
- Q4: Implement undo and exclusion pattern features.
- Ongoing: Collect and review user feedback, prioritize enhancements, and maintain robust test coverage.
