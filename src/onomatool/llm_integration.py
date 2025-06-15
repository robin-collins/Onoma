import base64
import json
import mimetypes
import os

import tiktoken

from onomatool.config import get_config
from onomatool.prompts import get_image_prompt, get_system_prompt, get_user_prompt

# Maximum tokens for LLM response - limits response to 100 tokens
MAX_TOKENS = 100

# Maximum characters to send to LLM (approx 65,535 tokens)
MAX_CONTENT_CHARS = 120_000

# Maximum consecutive digits allowed in a single word - prevents extremely long number sequences
MAX_CONSECUTIVE_DIGITS = 10


def generate_schema_patterns(min_words: int, max_words: int) -> dict:
    """
    Generate JSON schema patterns for all naming conventions based on min/max word counts.

    Args:
        min_words: Minimum number of words allowed (e.g., 5)
        max_words: Maximum number of words allowed (e.g., 15)

    Returns:
        Dictionary with schema patterns for each naming convention
    """
    if min_words < 1:
        min_words = 1
    if max_words < min_words:
        max_words = min_words

    # Calculate the quantifier range for regex patterns
    # For min_words=5, max_words=15: we need {4,14} (since first word is required)
    min_additional = max(0, min_words - 1)
    max_additional = max_words - 1

    quantifier = f"{{{min_additional},{max_additional}}}"

    # Use simple alphanumeric patterns - digit limiting will be handled via prompt engineering
    # JSON Schema regex has limited support for complex patterns, so we'll rely on LLM constraints
    word_pattern = r"[a-z0-9]+"
    camel_first_pattern = r"[a-z0-9]+"  # camelCase first word (lowercase start)
    camel_word_pattern = r"[A-Z][a-z0-9]*"  # camelCase subsequent words
    pascal_word_pattern = r"[A-Z][a-z0-9]*"  # PascalCase words
    natural_word_pattern = r"[A-Za-z0-9]+"  # Natural language words

    return {
        "snake_case": {
            "type": "json_schema",
            "json_schema": {
                "name": "suggestions",
                "schema": {
                    "type": "object",
                    "properties": {
                        "suggestions": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {
                                "type": "string",
                                "pattern": f"^{word_pattern}(_{word_pattern}){quantifier}$",
                                "maxLength": 128,
                            },
                        }
                    },
                    "required": ["suggestions"],
                    "additionalProperties": False,
                },
            },
        },
        "camelCase": {
            "type": "json_schema",
            "json_schema": {
                "name": "suggestions",
                "schema": {
                    "type": "object",
                    "properties": {
                        "suggestions": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {
                                "type": "string",
                                "pattern": f"^{camel_first_pattern}(?:{camel_word_pattern}){quantifier}$",
                                "maxLength": 128,
                            },
                        }
                    },
                    "required": ["suggestions"],
                    "additionalProperties": False,
                },
            },
        },
        "kebab-case": {
            "type": "json_schema",
            "json_schema": {
                "name": "suggestions",
                "schema": {
                    "type": "object",
                    "properties": {
                        "suggestions": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {
                                "type": "string",
                                "pattern": f"^{word_pattern}(-{word_pattern}){quantifier}$",
                                "maxLength": 128,
                            },
                        }
                    },
                    "required": ["suggestions"],
                    "additionalProperties": False,
                },
            },
        },
        "PascalCase": {
            "type": "json_schema",
            "json_schema": {
                "name": "suggestions",
                "schema": {
                    "type": "object",
                    "properties": {
                        "suggestions": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {
                                "type": "string",
                                "pattern": f"^{pascal_word_pattern}(?:{pascal_word_pattern}){quantifier}$",
                                "maxLength": 128,
                            },
                        }
                    },
                    "required": ["suggestions"],
                    "additionalProperties": False,
                },
            },
        },
        "dot.notation": {
            "type": "json_schema",
            "json_schema": {
                "name": "suggestions",
                "schema": {
                    "type": "object",
                    "properties": {
                        "suggestions": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {
                                "type": "string",
                                "pattern": f"^{word_pattern}(\\.{word_pattern}){quantifier}$",
                                "maxLength": 128,
                            },
                        }
                    },
                    "required": ["suggestions"],
                    "additionalProperties": False,
                },
            },
        },
        "natural language": {
            "type": "json_schema",
            "json_schema": {
                "name": "suggestions",
                "schema": {
                    "type": "object",
                    "properties": {
                        "suggestions": {
                            "type": "array",
                            "minItems": 3,
                            "maxItems": 3,
                            "items": {
                                "type": "string",
                                "pattern": f"^{natural_word_pattern}( {natural_word_pattern}){quantifier}$",
                                "maxLength": 128,
                            },
                        }
                    },
                    "required": ["suggestions"],
                    "additionalProperties": False,
                },
            },
        },
    }


def is_image_file(file_path: str) -> bool:
    """
    Return True if the file extension is an image type supported for LLM image input.
    Note: .svg is included because SVGs are rendered to PNG before LLM input.
    """
    ext = os.path.splitext(file_path)[1].lower()
    return ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg"}


def encode_image_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_suggestions(
    content: str,
    verbose: bool = False,
    file_path: str | None = None,
    config: dict | None = None,
) -> list[str]:
    """
    Query the configured LLM (OpenAI or Google) for filename suggestions using the appropriate JSON schema.

    Args:
        content: The file content to send to the LLM for analysis and suggestion.
        verbose: If True, print the LLM request and response for debugging.
        file_path: The path to the file being processed (used for image support).
        config: The configuration dictionary to use (if None, loads default config).

    Returns:
        List of filename suggestions (strings) as per the configured naming convention.

    Raises:
        RuntimeError: If the LLM call fails or the response does not match the schema.
    """
    if config is None:
        config = get_config()
    provider = config.get("default_provider", "openai")
    naming_convention = config.get("naming_convention", "snake_case")
    model = config.get("llm_model", "gpt-4o")
    min_words = config.get("min_filename_words", 5)
    max_words = config.get("max_filename_words", 15)

    # Generate schemas dynamically based on config
    schemas = generate_schema_patterns(min_words, max_words)
    schema = schemas.get(naming_convention, schemas["snake_case"])
    system_prompt = get_system_prompt(config)
    # Limit text content to prevent exceeding LLM context limits
    truncated_content = content[:MAX_CONTENT_CHARS]
    if len(content) > MAX_CONTENT_CHARS and verbose:
        pass

    # Detect if this is an image file
    is_image = file_path and is_image_file(file_path)
    image_message = None
    if is_image:
        ext = os.path.splitext(file_path)[1].lower()
        # Prevent sending raw SVGs directly to the LLM
        if ext == ".svg":
            raise RuntimeError(
                "Raw SVG files must not be sent to the LLM. Convert to PNG first."
            )
        # If the file is a PNG generated from an SVG, enforce PNG MIME type
        if ext == ".png":
            mime = "image/png"
        else:
            mime, _ = mimetypes.guess_type(file_path)
            if not mime:
                mime = "image/jpeg"
        base64_image = encode_image_base64(file_path)
        image_message = {
            "type": "input_image",
            "image_url": f"data:{mime};base64,{base64_image}",
        }

    if is_image:
        user_prompt = get_image_prompt(naming_convention, config)
    else:
        user_prompt = get_user_prompt(naming_convention, truncated_content, config)

    # MOCK PROVIDER: Always return static suggestions for tests
    if provider == "mock":
        if naming_convention == "snake_case":
            return ["mock_file_one", "mock_file_two", "mock_file_three"]
        if naming_convention == "camelCase":
            return ["mockFileOne", "mockFileTwo", "mockFileThree"]
        if naming_convention == "kebab-case":
            return ["mock-file-one", "mock-file-two", "mock-file-three"]
        if naming_convention == "PascalCase":
            return ["MockFileOne", "MockFileTwo", "MockFileThree"]
        if naming_convention == "dot.notation":
            return ["mock.file.one", "mock.file.two", "mock.file.three"]
        if naming_convention == "natural language":
            return ["Mock File One", "Mock File Two", "Mock File Three"]
        return ["mock_file_one", "mock_file_two", "mock_file_three"]

    if provider == "openai":
        try:
            import httpx
            from openai import OpenAI

            base_url = config.get("openai_base_url", "https://api.openai.com/v1")
            api_key = config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
            verify = True
            if base_url.startswith(
                ("http://", "https://10.", "https://127.", "https://localhost")
            ):
                verify = False
            client = OpenAI(
                base_url=base_url,
                api_key=api_key,
                http_client=httpx.Client(verify=verify),
            )
            if is_image and image_message:
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": image_message["image_url"]},
                            },
                        ],
                    },
                ]
            else:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            if verbose:

                def redact_message(msg, redact_text=True):
                    if isinstance(msg, dict):
                        msg = msg.copy()
                        # Redact image_url base64 in all nested structures
                        if msg.get("type") == "image_url":
                            if (
                                isinstance(msg["image_url"], dict)
                                and "url" in msg["image_url"]
                            ):
                                msg["image_url"] = {"url": "[[base64_image]]"}
                            elif isinstance(msg["image_url"], str):
                                msg["image_url"] = "[[base64_image]]"
                        # Optionally redact text content
                        if redact_text and msg.get("type") == "text":
                            msg["text"] = "[[file_content]]"
                        # Recursively redact lists in 'content'
                        if isinstance(msg.get("content"), list):
                            msg["content"] = [
                                redact_message(x, redact_text=redact_text)
                                for x in msg["content"]
                            ]
                        return msg
                    return msg

                def redact_messages(messages, redact_text=True):
                    if isinstance(messages, list):
                        return [
                            redact_message(m, redact_text=redact_text) for m in messages
                        ]
                    return messages

                redact_text = not is_image

                # Calculate character and token counts for the entire request
                sum(len(str(msg.get("content", ""))) for msg in messages)
                if is_image:
                    # For images, only count text content, not base64 image data
                    len(user_prompt)
                count_tokens_for_messages(messages, model)

                if redact_text:
                    pass
                else:
                    pass
            response = client.chat.completions.create(
                model=model,  # Now loaded from config
                messages=messages,
                response_format=schema,
                max_tokens=MAX_TOKENS,
            )
            if verbose:
                pass
            result = json.loads(response.choices[0].message.content)
            suggestions = result["suggestions"]
            if not (isinstance(suggestions, list) and len(suggestions) == 3):
                raise RuntimeError("LLM did not return exactly 3 suggestions.")
            return suggestions
        except Exception as err:
            raise RuntimeError(f"OpenAI LLM call failed: {err}") from err
    elif provider == "google":
        try:
            import google.generativeai as genai

            genai.configure(
                api_key=config.get("google_api_key") or os.environ.get("GOOGLE_API_KEY")
            )
            model_name = "gemini-pro"
            model = genai.GenerativeModel(model_name)

            # Configure generation settings with max_output_tokens
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=MAX_TOKENS
            )

            if verbose:
                # Calculate character and token counts for Google request
                len(user_prompt)
                count_text_tokens(
                    user_prompt, "gpt-4o"
                )  # Use gpt-4o encoding as approximation

            response = model.generate_content(
                user_prompt, generation_config=generation_config
            )
            import re

            if verbose:
                pass
            suggestions = re.findall(r'"([a-zA-Z0-9_\-\. ]{1,128})"', response.text)
            if len(suggestions) < 3:
                raise RuntimeError("Google LLM did not return enough suggestions.")
            return suggestions[:3]
        except Exception as err:
            raise RuntimeError(f"Google LLM call failed: {err}") from err
    else:
        raise RuntimeError(f"Unsupported provider: {provider}")


def count_tokens_for_messages(messages: list, model: str = "gpt-4o") -> int:
    """
    Count tokens for OpenAI chat completion messages using tiktoken.

    Based on OpenAI cookbook examples for counting tokens.

    Args:
        messages: List of messages in OpenAI format
        model: Model name to get appropriate encoding

    Returns:
        Number of tokens the messages will consume
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # If model not found, default to cl100k_base (used by gpt-4, gpt-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")

    # Token counting logic based on OpenAI cookbook
    if model in {
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        "gpt-4o-mini-2024-07-18",
        "gpt-4o-2024-08-06",
        "gpt-4o-2024-05-13",
        "gpt-4-turbo-2024-04-09",
        "gpt-4-1106-preview",
        "gpt-4-0125-preview",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        # Default for newer models like gpt-4o
        tokens_per_message = 3
        tokens_per_name = 1

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if key == "content":
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                elif isinstance(value, list):
                    # Handle multimodal content (text + images)
                    for item in value:
                        if item.get("type") == "text":
                            num_tokens += len(encoding.encode(item.get("text", "")))
                        # Note: image tokens are not counted by tiktoken
            else:
                num_tokens += len(encoding.encode(str(value)))
            if key == "name":
                num_tokens += tokens_per_name

    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def count_text_tokens(text: str, model: str = "gpt-4o") -> int:
    """
    Count tokens for a text string using tiktoken.

    Args:
        text: Text to count tokens for
        model: Model name to get appropriate encoding

    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # If model not found, default to cl100k_base
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))
