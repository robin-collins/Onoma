import base64
import json
import mimetypes
import os

from onomatool.config import get_config
from onomatool.prompts import get_image_prompt, get_system_prompt, get_user_prompt


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
    content: str, verbose: bool = False, file_path: str = None, config: dict = None
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
    schemas = {
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
                                "pattern": "^[a-z0-9]+(_[a-z0-9]+)*$",
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
                                "pattern": "^[a-z]+(?:[A-Z][a-z0-9]*)*$",
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
                                "pattern": "^[a-z0-9]+(-[a-z0-9]+)*$",
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
                                "pattern": "^[A-Z][a-z0-9]*(?:[A-Z][a-z0-9]*)*$",
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
                                "pattern": "^[a-z0-9]+(\\.[a-z0-9]+)*$",
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
                                "pattern": "^[A-Za-z0-9]+( [A-Za-z0-9]+)*$",
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
    schema = schemas.get(naming_convention, schemas["snake_case"])
    system_prompt = get_system_prompt(config)
    # Limit text content to 200,000 characters approx 65535 tokens
    max_content_chars = 195_000
    truncated_content = content[:max_content_chars]

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
        elif naming_convention == "camelCase":
            return ["mockFileOne", "mockFileTwo", "mockFileThree"]
        elif naming_convention == "kebab-case":
            return ["mock-file-one", "mock-file-two", "mock-file-three"]
        elif naming_convention == "PascalCase":
            return ["MockFileOne", "MockFileTwo", "MockFileThree"]
        elif naming_convention == "dot.notation":
            return ["mock.file.one", "mock.file.two", "mock.file.three"]
        elif naming_convention == "natural language":
            return ["Mock File One", "Mock File Two", "Mock File Three"]
        else:
            return ["mock_file_one", "mock_file_two", "mock_file_three"]

    if provider == "openai":
        try:
            import httpx
            from openai import OpenAI

            base_url = config.get("openai_base_url", "https://api.openai.com/v1")
            api_key = config.get("openai_api_key") or os.environ.get("OPENAI_API_KEY")
            verify = True
            if (
                base_url.startswith("http://")
                or base_url.startswith("https://10.")
                or base_url.startswith("https://127.")
                or base_url.startswith("https://localhost")
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
                print("\n[LLM CONFIGURATION]")
                print(f"base_url: {base_url}")
                print(f"model: {model}")
                print("json_schema:")
                print(json.dumps(schema, indent=2))
                print("\n[LLM REQUEST]")
                print("System Prompt:", system_prompt)
                if redact_text:
                    print(
                        "User Prompt:",
                        "[[file_content]]"
                        if is_image or len(truncated_content) > 200
                        else user_prompt,
                    )
                else:
                    print("User Prompt:", user_prompt)
                print(
                    "Messages:",
                    json.dumps(
                        redact_messages(messages, redact_text=redact_text), indent=2
                    ),
                )
                print("Schema:", json.dumps(schema, indent=2))
            response = client.chat.completions.create(
                model=model,  # Now loaded from config
                messages=messages,
                response_format=schema,
            )
            if verbose:
                print("\n[LLM RAW RESPONSE]")
                print(response)
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
            model = "gemini-pro"
            if verbose:
                print("\n[LLM CONFIGURATION]")
                print("base_url: Google Generative AI")
                print(f"model: {model}")
                print("json_schema:")
                print(json.dumps(schema, indent=2))
            response = model.generate_content(user_prompt)
            import re

            if verbose:
                print("\n[LLM REQUEST]")
                print("System Prompt:", system_prompt)
                print("User Prompt:", user_prompt)
                print("Schema:", json.dumps(schema, indent=2))
                print("\n[LLM RAW RESPONSE]")
                print(response)
            suggestions = re.findall(r'"([a-zA-Z0-9_\-\. ]{1,128})"', response.text)
            if len(suggestions) < 3:
                raise RuntimeError("Google LLM did not return enough suggestions.")
            return suggestions[:3]
        except Exception as err:
            raise RuntimeError(f"Google LLM call failed: {err}") from err
    else:
        raise RuntimeError(f"Unsupported provider: {provider}")
