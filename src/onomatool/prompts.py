"""
Prompt templates for OnomaTool LLM integration.
These can be overridden via the .onomarc config file.
"""

from onomatool.config import get_config


def get_system_prompt() -> str:
    config = get_config()
    return config.get("system_prompt") or DEFAULT_SYSTEM_PROMPT


def get_user_prompt(naming_convention: str, content: str) -> str:
    config = get_config()
    template = config.get("user_prompt") or DEFAULT_USER_PROMPT
    return template.format(naming_convention=naming_convention, content=content)


def get_image_prompt(naming_convention: str) -> str:
    config = get_config()
    template = config.get("image_prompt") or DEFAULT_IMAGE_PROMPT
    return template.format(naming_convention=naming_convention)


DEFAULT_SYSTEM_PROMPT = "You are a file naming suggestion assistant."

DEFAULT_USER_PROMPT = (
    "You are an expert file naming assistant. Your task is to suggest 3 file names for the "
    "provided file content, following a specific naming convention. Only return the suggestions "
    "as specified in the JSON schema. When providing suggestions consider the who, what, when, "
    "where, why, and how of the file content, its purpose or inteded use. A good file name should "
    "be concise, descriptive, and easy to understand and be between five and ten words in length. "
    "Take note of indicators of the file content, such as the date, time, location, and other "
    "relevant information like chat transcripts, source code bundles, file lists or file tree's. "
    "Avoid assumptions unless other indicators are ambiguous or not present. Content that is "
    "multiple files listed inside markdown triple backticks or inside XML tags is a codebase "
    "prepared for ingestion by an LLM, attempt to identify the project or codebase name where "
    "possible.\n\nCONTENT:\n{content}"
)

DEFAULT_IMAGE_PROMPT = (
    "You are an expert file naming assistant. Your task is to suggest 3 file names for the provided "
    "image, following a specific naming convention. Your goal is to create concise, descriptive, and "
    "easily understandable file names that accurately represent the visual content and context of the "
    "image.\n\nFirst, carefully analyze the provided image.\n\nYou must follow the {naming_convention} "
    "naming convention when creating your suggestions.\n\n## Visual Analysis Guidelines:\n\nWhen analyzing "
    "the image, examine these elements systematically:\n- Primary subjects: People, objects, locations, or "
    "focal points\n- Setting and context: Indoor/outdoor, specific locations, environments\n- Activities or "
    "actions: What is happening in the image\n- Text content: Any visible text, logos, signs, or written "
    "information\n- Technical aspects: Screenshot, diagram, chart, photo type, etc.\n- Visual style: "
    "Professional, casual, artistic, technical, documentary\n- Temporal indicators: Time of day, season, or "
    "date information if visible\n\n## Enhanced Analysis Guidelines:\n\nWhen analyzing the image, look for "
    "identifying information that could improve specificity:\n- Brand names, logos, or company identifiers "
    "visible in the image\n- Application interfaces, software names, or system identifiers\n- Location names, "
    "landmarks, or geographic identifiers\n- Event names, occasions, or contextual markers\n- Product names, "
    "model numbers, or specific item identifiers\n- Dates, timestamps, or other temporal information visible "
    "in the image\n\n## File Naming Criteria:\n\n1. Prioritize specific identifiers when clearly visible "
    "(brands, locations, applications, products)\n2. Be descriptive about visual content and context\n3. "
    "Include relevant details (setting, activity, style, technical type)\n4. Be between five and ten words "
    "in length\n5. Consider the who, what, when, where, why, and how of the visual content\n6. Use clear, "
    "descriptive terminology\n7. Balance specificity with broad applicability\n\n## Image-Specific "
    "Considerations:\n- For screenshots: Include application name if identifiable, interface type, or "
    "function\n- For photographs: Include subject, setting, activity, or notable visual elements\n- For "
    "diagrams/charts: Include data type, purpose, or subject matter\n- For documents: Include document type, "
    "source, or content category\n- For logos/graphics: Include brand, style, or usage context\n- Avoid "
    "overly generic terms unless no specific details are discernible\n\nOnly return the suggestions as "
    "specified in the JSON schema.\n\nRemember:\n- Only return the suggestions as specified in the JSON "
    "schema\n- Do not include any explanations or additional text outside the JSON structure\n- Ensure that "
    "each suggestion strictly follows the provided naming convention\n- Double-check that your suggestions "
    "accurately reflect the visual content and any identifiable context\n\nNow, based on the given image and "
    "naming convention, generate 3 appropriate file name suggestions that capture both the visual content and "
    "any identifiable context."
)
