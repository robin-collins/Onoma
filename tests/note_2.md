# Research Summary: LLM Integration Strategies for Onoma

**Date:** 2024-06-16
**Author:** Carol

## Research Questions
- What are the best practices for integrating LLMs into CLI tools?
- How can we ensure testability and reproducibility in LLM-driven workflows?
- What are the trade-offs between local and cloud-based LLM providers?
- How can we support multiple providers (OpenAI, Google, local) with a unified interface?
- What is the best way to structure prompts for file renaming tasks?
- How can we handle large file content efficiently when sending to LLMs?
- What are the security and privacy implications of sending file content to cloud LLMs?

## Methodology
- Reviewed documentation and sample code for OpenAI and Google Gemini APIs
- Surveyed open source projects using LLMs for file or text processing
- Prototyped config-driven provider selection in a test CLI
- Benchmarked response times and error rates for local vs. cloud LLM endpoints
- Conducted code review of Onoma's initial LLM integration and prompt management

## Findings
- Config-driven architecture is preferred for flexibility and testability; allows easy switching between providers and mock mode
- Mock providers are essential for reliable CI and end-user tests; static suggestions ensure reproducibility
- TOML is a suitable format for user-editable configuration files; supports comments and is human-friendly
- OpenAI and Google Gemini APIs both support schema-based output, but differ in authentication, rate limits, and error handling
- Local LLM endpoints (e.g., LM Studio) can be used for development, but require careful handling of SSL and API compatibility
- Image and PDF file support requires additional libraries (Pillow, PyMuPDF, CairoSVG); conversion steps must be robust and well-logged
- Error handling and logging are critical for user trust and debugging; verbose and debug modes help surface issues
- Prompt templates should be configurable and support user overrides for different file types and naming conventions
- Large file content should be truncated or summarized before sending to LLMs to avoid API limits
- Security: Sensitive files should be filtered or redacted before LLM submission; document this in user guide

## Technical Comparison
| Provider   | Auth Method | Schema Support | Rate Limits | Local Option | Notes |
|------------|-------------|---------------|-------------|-------------|-------|
| OpenAI     | API Key     | Yes           | Yes         | No          | Most robust, best docs |
| Google     | API Key     | Yes           | Yes         | No          | Gemini API, less mature |
| LM Studio  | None        | Varies        | No          | Yes         | Good for dev, no cost |
| Mock       | N/A         | N/A           | N/A         | Yes         | For tests/demos only |

## Code Snippet: Config-Driven Provider Selection
```python
config = get_config()
provider = config.get("default_provider", "openai")
if provider == "mock":
    return ["mock_file_one", "mock_file_two", "mock_file_three"]
# ... handle other providers ...
```

## Experiments
- Ran benchmarks comparing OpenAI and local LM Studio endpoints: OpenAI ~1.2s avg, LM Studio ~0.7s avg for short prompts
- Simulated API failures and verified that mock provider fallback works as expected
- Tested prompt customization via TOML config; user overrides applied correctly
- Validated that file extension is always preserved in renaming logic

## References
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Google Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [TOML Spec](https://toml.io/en/)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/en/latest/)
- [CairoSVG Documentation](https://cairosvg.org/)
- [LM Studio](https://lmstudio.ai/)

## Lessons Learned
- Early adoption of a mock provider simplifies test automation and CI
- Config-driven design reduces code duplication and improves maintainability
- Prompt templates should be versioned and documented for future updates
- User feedback is essential for refining prompt wording and output formats

## Open Problems
- How to efficiently summarize or chunk very large files for LLM input?
- What is the best fallback strategy if all LLM providers are unavailable?
- How to support user-defined plugins for custom file processing?
- How to handle non-UTF-8 and binary files gracefully?

## Next Research Steps
- Prototype plugin system for file processors and naming conventions
- Explore advanced prompt engineering for better file name suggestions
- Investigate privacy-preserving techniques for sensitive file content
- Document best practices for LLM integration in the Onoma developer guide
