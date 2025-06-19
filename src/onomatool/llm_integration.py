import base64
import json
import mimetypes
import os

import tiktoken

from onomatool.config import get_config
from onomatool.models import (
    generate_json_schema_from_model,
    get_model_for_naming_convention,
)
from onomatool.prompts import get_image_prompt, get_system_prompt, get_user_prompt

# Maximum tokens for LLM response - limits response to 100 tokens
MAX_TOKENS = 100

# Maximum characters to send to LLM (approx 65,535 tokens)
MAX_CONTENT_CHARS = 120_000

# Maximum consecutive digits allowed in a single word - prevents extremely long number sequences
MAX_CONSECUTIVE_DIGITS = 10


def get_pydantic_model_and_schema(naming_convention: str) -> tuple:
    """
    Get the Pydantic model and JSON schema for a given naming convention.

    Args:
        naming_convention: The naming convention string (e.g., "snake_case")

    Returns:
        Tuple of (pydantic_model_class, json_schema_dict)
    """
    try:
        model_class = get_model_for_naming_convention(naming_convention)
        json_schema = generate_json_schema_from_model(model_class)
        return model_class, json_schema
    except ValueError:
        # Fallback to snake_case if naming convention is not supported
        model_class = get_model_for_naming_convention("snake_case")
        json_schema = generate_json_schema_from_model(model_class)
        return model_class, json_schema


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
    verbose_level: int = 0,
    file_path: str | None = None,
    config: dict | None = None,
) -> list[str]:
    """
    Query the configured LLM (OpenAI or Google) for filename suggestions using the appropriate JSON schema.

    Args:
        content: The file content to send to the LLM for analysis and suggestion.
        verbose_level: Verbosity level (0=none, 1=basic debug, 2=full debug).
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

    # Get Pydantic model and JSON schema for the naming convention
    pydantic_model, json_schema = get_pydantic_model_and_schema(naming_convention)
    system_prompt = get_system_prompt(config)
    # Limit text content to prevent exceeding LLM context limits
    truncated_content = content[:MAX_CONTENT_CHARS]
    if len(content) > MAX_CONTENT_CHARS and verbose_level > 0:
        print(
            f"[DEBUG] Content truncated from {len(content)} to {MAX_CONTENT_CHARS} characters"
        )

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

            # Check if we should use Azure OpenAI
            use_azure = config.get("use_azure_openai", False)

            if use_azure:
                # Azure OpenAI configuration
                azure_endpoint = config.get("azure_openai_endpoint") or os.environ.get(
                    "AZURE_OPENAI_ENDPOINT"
                )
                azure_api_key = config.get("azure_openai_api_key") or os.environ.get(
                    "AZURE_OPENAI_API_KEY"
                )
                azure_api_version = config.get("azure_openai_api_version", "2024-02-01")
                azure_deployment = config.get(
                    "azure_openai_deployment"
                ) or os.environ.get("AZURE_OPENAI_DEPLOYMENT")

                if not azure_endpoint:
                    raise RuntimeError(
                        "Azure OpenAI endpoint is required when use_azure_openai is True"
                    )
                if not azure_api_key:
                    raise RuntimeError(
                        "Azure OpenAI API key is required when use_azure_openai is True"
                    )
                if not azure_deployment:
                    raise RuntimeError(
                        "Azure OpenAI deployment name is required when use_azure_openai is True"
                    )

                # For Azure, we override the model with the deployment name
                model = azure_deployment

                from openai import AzureOpenAI

                client = AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_key=azure_api_key,
                    api_version=azure_api_version,
                )
            else:
                # Standard OpenAI configuration
                base_url = config.get("openai_base_url", "https://api.openai.com/v1")
                api_key = config.get("openai_api_key") or os.environ.get(
                    "OPENAI_API_KEY"
                )
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
            if verbose_level > 0:
                # Print basic configuration details for -v
                if use_azure:
                    print("[DEBUG] Using Azure OpenAI")
                    print(f"[DEBUG] Azure endpoint: {azure_endpoint}")
                    print(f"[DEBUG] Azure deployment: {azure_deployment}")
                    print(f"[DEBUG] Azure API version: {azure_api_version}")
                else:
                    print("[DEBUG] Using OpenAI")
                    print(f"[DEBUG] Base URL: {base_url}")
                print(f"[DEBUG] Model: {model}")
                print(f"[DEBUG] Pydantic Model: {pydantic_model.__name__}")

                # Print detailed schema and configuration for -vv only
                if verbose_level > 1:
                    print(f"[DEBUG] JSON Schema: {json.dumps(json_schema, indent=2)}")
                    print(f"[DEBUG] Max tokens: {MAX_TOKENS}")
                    print(f"[DEBUG] Min filename words: {min_words}")
                    print(f"[DEBUG] Max filename words: {max_words}")

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

                    # Show detailed request/response info only for -vv

                if verbose_level > 1:
                    redact_text = not is_image

                    # Calculate character and token counts for the entire request
                    total_chars = sum(
                        len(str(msg.get("content", ""))) for msg in messages
                    )
                    if is_image:
                        # For images, only count text content, not base64 image data
                        total_chars = len(user_prompt)
                    total_tokens = count_tokens_for_messages(messages, model)

                    print(f"[DEBUG] Total characters in request: {total_chars}")
                    print(f"[DEBUG] Estimated tokens: {total_tokens}")

                    redacted_messages = redact_messages(
                        messages, redact_text=redact_text
                    )
                    print(
                        f"[DEBUG] Messages: {json.dumps(redacted_messages, indent=2)}"
                    )

                    if redact_text:
                        print("[DEBUG] Text content redacted as [[file_content]]")
                    else:
                        print(
                            "[DEBUG] Image content - text not redacted, base64 images redacted as [[base64_image]]"
                        )
            # Try to use structured output with Pydantic first
            try:
                response = client.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    response_format=pydantic_model,
                    max_tokens=MAX_TOKENS,
                )
                parsed_result = response.choices[0].message.parsed
                if parsed_result is None:
                    raise RuntimeError("Structured output parsing failed")

                if verbose_level > 0:
                    print("[DEBUG] Used structured output with Pydantic model")
                    print(f"[DEBUG] Response: suggestions={parsed_result.suggestions}")

                return parsed_result.suggestions

            except Exception as structured_error:
                if verbose_level > 0:
                    print(f"[DEBUG] Structured output failed: {structured_error}")
                    print("[DEBUG] Falling back to JSON schema approach")

                # Fallback to traditional JSON schema approach
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    response_format=json_schema,
                    max_tokens=MAX_TOKENS,
                )
                result = json.loads(response.choices[0].message.content)
                suggestions = result["suggestions"]

                if verbose_level > 0:
                    print("[DEBUG] Used JSON Schema fallback")
                    print(f"[DEBUG] Response: suggestions={suggestions}")

                if verbose_level > 1:
                    print(
                        f"[DEBUG] Full response content: {response.choices[0].message.content}"
                    )

                if not (isinstance(suggestions, list) and len(suggestions) == 3):
                    raise RuntimeError(
                        "LLM did not return exactly 3 suggestions."
                    ) from None
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

            if verbose_level > 1:
                # Calculate character and token counts for Google request
                total_chars = len(user_prompt)
                total_tokens = count_text_tokens(
                    user_prompt, "gpt-4o"
                )  # Use gpt-4o encoding as approximation
                print(f"[DEBUG] Total characters in request: {total_chars}")
                print(f"[DEBUG] Estimated tokens: {total_tokens}")

            response = model.generate_content(
                user_prompt, generation_config=generation_config
            )
            import re

            suggestions = re.findall(r'"([a-zA-Z0-9_\-\. ]{1,128})"', response.text)

            if verbose_level > 0:
                print(f"[DEBUG] Response: suggestions={suggestions[:3]}")

            if verbose_level > 1:
                print(f"[DEBUG] Full response text: {response.text}")

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
