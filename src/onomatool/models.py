"""
Pydantic models for structured LLM responses.

These models define the structure for filename suggestions returned by LLMs,
ensuring type safety and validation. The models are used with OpenAI's
structured output feature via client.beta.chat.completions.parse().
"""

from pydantic import BaseModel, Field, field_validator


class FilenameSuggestions(BaseModel):
    """
    Model for filename suggestions returned by LLMs.

    This model enforces that exactly 3 suggestions are returned,
    with each suggestion being a valid filename string.
    """

    suggestions: list[str] = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Exactly 3 filename suggestions based on the content analysis",
    )

    @field_validator("suggestions")
    @classmethod
    def validate_suggestions(cls, v):
        """Validate that all suggestions are non-empty strings with reasonable length."""
        if len(v) != 3:
            raise ValueError("Must provide exactly 3 suggestions")

        for suggestion in v:
            if not isinstance(suggestion, str):
                raise ValueError("Each suggestion must be a string")
            if not suggestion.strip():
                raise ValueError("Suggestions cannot be empty or whitespace-only")
            if len(suggestion) > 128:
                raise ValueError("Suggestions must be 128 characters or less")

        return v


class SnakeCaseFilenameSuggestions(FilenameSuggestions):
    """Snake case filename suggestions (e.g., my_document_file)."""

    @field_validator("suggestions")
    @classmethod
    def validate_snake_case(cls, v):
        """Validate that suggestions follow snake_case pattern."""
        v = super().validate_suggestions(v)

        import re

        snake_case_pattern = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")

        for suggestion in v:
            if not snake_case_pattern.match(suggestion):
                raise ValueError(f"'{suggestion}' is not valid snake_case format")

        return v


class CamelCaseFilenameSuggestions(FilenameSuggestions):
    """Camel case filename suggestions (e.g., myDocumentFile)."""

    @field_validator("suggestions")
    @classmethod
    def validate_camel_case(cls, v):
        """Validate that suggestions follow camelCase pattern."""
        v = super().validate_suggestions(v)

        import re

        camel_case_pattern = re.compile(r"^[a-z0-9]+([A-Z][a-z0-9]*)*$")

        for suggestion in v:
            if not camel_case_pattern.match(suggestion):
                raise ValueError(f"'{suggestion}' is not valid camelCase format")

        return v


class KebabCaseFilenameSuggestions(FilenameSuggestions):
    """Kebab case filename suggestions (e.g., my-document-file)."""

    @field_validator("suggestions")
    @classmethod
    def validate_kebab_case(cls, v):
        """Validate that suggestions follow kebab-case pattern."""
        v = super().validate_suggestions(v)

        import re

        kebab_case_pattern = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

        for suggestion in v:
            if not kebab_case_pattern.match(suggestion):
                raise ValueError(f"'{suggestion}' is not valid kebab-case format")

        return v


class PascalCaseFilenameSuggestions(FilenameSuggestions):
    """Pascal case filename suggestions (e.g., MyDocumentFile)."""

    @field_validator("suggestions")
    @classmethod
    def validate_pascal_case(cls, v):
        """Validate that suggestions follow PascalCase pattern."""
        v = super().validate_suggestions(v)

        import re

        pascal_case_pattern = re.compile(r"^[A-Z][a-z0-9]*([A-Z][a-z0-9]*)*$")

        for suggestion in v:
            if not pascal_case_pattern.match(suggestion):
                raise ValueError(f"'{suggestion}' is not valid PascalCase format")

        return v


class DotNotationFilenameSuggestions(FilenameSuggestions):
    """Dot notation filename suggestions (e.g., my.document.file)."""

    @field_validator("suggestions")
    @classmethod
    def validate_dot_notation(cls, v):
        """Validate that suggestions follow dot.notation pattern."""
        v = super().validate_suggestions(v)

        import re

        dot_notation_pattern = re.compile(r"^[a-z0-9]+(\.[a-z0-9]+)*$")

        for suggestion in v:
            if not dot_notation_pattern.match(suggestion):
                raise ValueError(f"'{suggestion}' is not valid dot.notation format")

        return v


class NaturalLanguageFilenameSuggestions(FilenameSuggestions):
    """Natural language filename suggestions (e.g., My Document File)."""

    @field_validator("suggestions")
    @classmethod
    def validate_natural_language(cls, v):
        """Validate that suggestions follow natural language pattern."""
        v = super().validate_suggestions(v)

        import re

        natural_language_pattern = re.compile(r"^[A-Za-z0-9]+( [A-Za-z0-9]+)*$")

        for suggestion in v:
            if not natural_language_pattern.match(suggestion):
                raise ValueError(f"'{suggestion}' is not valid natural language format")

        return v


# Mapping of naming conventions to their corresponding Pydantic models
NAMING_CONVENTION_MODELS = {
    "snake_case": SnakeCaseFilenameSuggestions,
    "camelCase": CamelCaseFilenameSuggestions,
    "kebab-case": KebabCaseFilenameSuggestions,
    "PascalCase": PascalCaseFilenameSuggestions,
    "dot.notation": DotNotationFilenameSuggestions,
    "natural language": NaturalLanguageFilenameSuggestions,
}


def get_model_for_naming_convention(
    naming_convention: str,
) -> type[FilenameSuggestions]:
    """
    Get the appropriate Pydantic model for a given naming convention.

    Args:
        naming_convention: The naming convention string (e.g., "snake_case")

    Returns:
        The corresponding Pydantic model class

    Raises:
        ValueError: If the naming convention is not supported
    """
    if naming_convention not in NAMING_CONVENTION_MODELS:
        raise ValueError(f"Unsupported naming convention: {naming_convention}")

    return NAMING_CONVENTION_MODELS[naming_convention]


def generate_json_schema_from_model(model_class: type[BaseModel]) -> dict:
    """
    Generate a JSON schema from a Pydantic model for fallback compatibility.

    This is used when the LLM provider doesn't support Pydantic structured output
    but still needs a JSON schema for response formatting.

    Args:
        model_class: The Pydantic model class

    Returns:
        A dictionary containing the JSON schema in OpenAI format
    """
    schema = model_class.model_json_schema()

    # Convert Pydantic schema to OpenAI structured output format
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "suggestions",
            "schema": schema,
        },
    }
