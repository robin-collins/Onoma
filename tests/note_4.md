# Bug Report: Mock Config Not Honored by CLI

**Date:** 2024-06-15
**Reporter:** Dave

## Environment
- OS: Ubuntu 22.04 (WSL2)
- Python: 3.13.1 (venv: Onoma)
- Onoma version: 0.1.0
- CLI location: `src/onomatool/cli.py`
- Config file: `tests/mock_config.toml`
- Test files: `tests/note_0.md`, `tests/note_1.md`, ...
- LLM Integration: `src/onomatool/llm_integration.py`
- Prompt Management: `src/onomatool/prompts.py`
- Test runner: pytest 8.4.0
- CI: GitHub Actions (ubuntu-latest)
- Shell: /usr/bin/bash
- Editor: VS Code (WSL Remote)

## Steps to Reproduce
1. Create a mock config file with `default_provider = "mock"` and static suggestions.
2. Place test markdown files in the `tests/` directory.
3. Run the CLI with `--config tests/mock_config.toml` and a test markdown file:
   ```bash
   python src/onomatool/cli.py tests/note_0.md --config tests/mock_config.toml
   ```
4. Observe the output and the renamed file in the directory.
5. Run the end-user usage tests:
   ```bash
   pytest tests/test_usage_enduser.py
   ```

## Expected Behavior
- The CLI should use the mock provider and always return static suggestions (e.g., `mock_file_one`).
- The renamed file should match the mock suggestion, e.g., `mock_file_one.md`.
- All tests should pass, confirming the CLI honors the mock config.
- Logs should indicate that the mock provider was selected and used.

## Actual Behavior
- The CLI used a real LLM suggestion (`robincollins_website_daily_report.md`) instead of the mock.
- Tests failed because the output did not match the expected mock file name.
- Output example:
  ```
  Renamed 'note_0.md' to 'robincollins_website_daily_report.md'
  ```
- Test failure example:
  ```
  AssertionError: assert os.path.exists('/tmp/tmpc2s084ud/mock_file_one.md')
  ```
- Logs did not indicate use of the mock provider.

## Investigation
- Verified that `mock_config.toml` was loaded and contained the correct `default_provider` setting.
- Traced CLI logic: config was loaded in `main()`, but not passed to `get_suggestions` or prompt helpers.
- Found that `get_suggestions` in `llm_integration.py` always loaded the default config, ignoring the CLI's loaded config.
- Confirmed that patching `get_suggestions` in tests did not affect subprocesses, due to process isolation.
- Reviewed project rules: mock provider must always return static suggestions for tests and demos.
- Examined test logs and CI output for discrepancies in config usage.
- Discussed with Bob and Carol; confirmed similar issues in their local environments.

## Root Cause Analysis
- The config loaded by the CLI was not being passed to the LLM integration layer or prompt helpers.
- As a result, `get_suggestions` used the default config, not the test config, and called the real LLM provider.
- This caused the CLI to ignore the mock provider and break test isolation, leading to non-deterministic test results.
- The bug was masked in some local runs due to environment variable overrides, but consistently failed in CI.

## Resolution
- Refactored CLI and LLM integration to always pass the loaded config to `get_suggestions` and all prompt helpers.
- Updated all calls to `get_suggestions` in `cli.py` to include the config argument.
- Updated `prompts.py` to accept and use the config argument for all prompt helpers.
- Added explicit logging of provider selection in verbose/debug mode.
- Verified that tests now pass and mock provider is honored in all scenarios.
- Updated documentation to clarify config flow and provider selection.

## Verification Steps
1. Run the CLI with the mock config and verify the renamed file matches the static mock suggestion.
2. Run the end-user usage tests and confirm all tests pass.
3. Check logs for correct provider selection and static suggestions.
4. Review code to ensure config is always passed through all relevant layers.
5. Test with both real and mock providers to confirm correct behavior.
6. Run CI pipeline and verify all tests pass in clean environments.

## Related Issues
- #23: Test isolation for LLM provider selection
- #27: Config not honored in subprocess tests
- #31: Improve error messages for config loading failures
- #35: Add logging for provider selection in verbose mode

## Future Prevention
- Add regression tests to ensure mock provider is always honored in test mode.
- Document config flow and provider selection in developer guide.
- Require code review for all changes to config and LLM integration logic.
- Add CI checks for config-driven test scenarios.
- Encourage use of verbose/debug mode in all test runs.
- Schedule periodic reviews of config and provider logic.

## Lessons Learned
- Always pass config explicitly through all layers to avoid hidden dependencies.
- Test isolation is critical for reliable CI and reproducible results.
- Verbose logging helps surface subtle bugs in provider selection and config usage.
- Collaboration and code review accelerate bug discovery and resolution.

## Status
- [x] Fixed
- [ ] Needs further review
