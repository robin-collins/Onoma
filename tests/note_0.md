# Project Meeting Notes

**Date:** 2024-06-18
**Attendees:** Alice (Lead), Bob (LLM Integration), Carol (QA/Docs), Dave (File Processing), Eve (UX), Frank (DevOps)

## Agenda
- Project introduction and vision
- Review of competitive landscape
- Requirements gathering
- User personas and use cases
- Team assignments and responsibilities
- Technical architecture overview
- Timeline, milestones, and deliverables
- Risk assessment and mitigation
- Next steps and scheduling
- Open issues and Q&A

## Discussion

### 1. Project Introduction and Vision
- Alice presented the vision for Onoma: an AI-powered tool to automate and standardize file naming for knowledge workers, researchers, and developers.
- The tool will leverage LLMs to generate context-aware, convention-compliant file names for a wide range of file types.
- Emphasis on extensibility, testability, and ease of integration into existing workflows.

### 2. Competitive Landscape
- Bob shared a review of existing tools (e.g., Namexif, FileBot, custom scripts) and highlighted gaps: lack of AI, poor CLI support, limited file type handling.
- Team agreed Onoma should focus on LLM-driven suggestions, robust CLI, and support for images, PDFs, and codebases.

### 3. Requirements Gathering
- Carol led a brainstorming session on must-have features:
  - CLI with dry-run, interactive, and debug modes
  - Configurable naming conventions (snake_case, camelCase, PascalCase, etc.)
  - TOML-based config with override support
  - Mock LLM provider for CI and demos
  - Logging, error handling, and verbose/debug output
  - Support for batch processing and recursive directory traversal
  - Output preview and export options
- Dave added requirements for image/PDF/SVG processing, including temp file management and conversion utilities.
- Eve suggested a future GUI/web interface for non-CLI users.

### 4. User Personas and Use Cases
- Alice described three primary personas:
  - Researcher: Needs to organize large sets of scanned documents and notes
  - Developer: Wants to standardize codebase and documentation file names
  - Knowledge worker: Handles mixed media (images, PDFs, screenshots) and needs batch renaming
- Use cases discussed:
  - Renaming meeting notes, reports, and research summaries
  - Organizing scanned receipts and contracts
  - Standardizing exported images and screenshots

### 5. Team Assignments and Responsibilities
- Alice: Project lead, CLI architecture, milestone tracking
- Bob: LLM integration, config management, provider abstraction
- Carol: Test design, documentation, user guides
- Dave: File processing, image/PDF/SVG handling, temp file utilities
- Eve: UX research, future GUI planning, user feedback
- Frank: DevOps, CI/CD, test automation, release management

### 6. Technical Architecture Overview
- Bob presented a draft architecture:
  - Modular CLI entrypoint with argparse
  - Config loader supporting overrides and environment variables
  - File dispatcher for type-specific processing
  - LLM integration layer with provider abstraction (OpenAI, Google, mock)
  - Prompt management for system/user/image prompts
  - Utilities for image/PDF/SVG conversion and temp file management
  - Test suite with pytest, mock config, and sample files
- Discussion on extensibility for future providers and file types

### 7. Timeline, Milestones, and Deliverables
- Week 1: CLI skeleton, config loader, initial tests, repo setup
- Week 2: LLM integration, file dispatcher, basic renaming logic
- Week 3: Image/PDF/SVG support, advanced prompts, error handling
- Week 4: End-user tests, documentation, release prep
- Deliverables: CLI tool, config samples, test suite, user docs, release notes

### 8. Risk Assessment and Mitigation
- Risks identified:
  - LLM API changes or rate limits (Mitigation: mock provider, config abstraction)
  - File permission issues on different OSes (Mitigation: robust error handling, test matrix)
  - Image/PDF conversion library compatibility (Mitigation: dependency checks, fallback logic)
  - User confusion over naming conventions (Mitigation: clear docs, examples, interactive mode)
- Frank to draft a risk register and update as project progresses

### 9. Next Steps and Scheduling
- Alice to set up project repo and initial file structure
- Bob to draft LLM integration plan and config schema
- Carol to outline test scenarios and documentation structure
- Dave to research and prototype image/PDF/SVG processing utilities
- Eve to prepare user interview questions for feedback
- Frank to configure CI/CD and test automation
- Next meeting scheduled for 2024-06-25

### 10. Open Issues and Q&A
- How to handle very large files or directories? (To be researched)
- Should we support cloud storage integration in v1? (Deferred)
- What is the minimum Python version? (Consensus: 3.9+)
- How to handle non-UTF-8 files? (Add to test cases)
- Q&A session with team; all questions documented in project wiki

## Action Items
- [x] Alice to create project repo and share with team
- [x] Bob to draft LLM integration plan
- [ ] Carol to outline test scenarios
- [ ] Dave to research image/PDF processing libraries
- [ ] Eve to prepare user interview questions
- [ ] Frank to set up CI/CD pipeline
- [ ] All to review and comment on initial architecture doc

## Summary
The kickoff meeting established a clear vision, detailed requirements, and a collaborative plan for Onoma. The team is aligned on priorities: robust CLI, flexible config, testability, and comprehensive file type support. Risks and open issues were identified, and next steps assigned. The next meeting will review progress on initial modules, integration plans, and user feedback preparation.

## Follow-up Questions
- What is the best way to support custom user prompts for different file types?
- How should we handle LLM API failures gracefully in batch mode?
- Should we allow user-defined plugins for file processing?

## Risks
- LLM API instability
- Dependency compatibility
- User adoption and onboarding

## Open Issues
- Large file handling
- Cloud integration
- Non-UTF-8 file support
