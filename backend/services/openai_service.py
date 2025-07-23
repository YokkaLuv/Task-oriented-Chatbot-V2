import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load API key từ file .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_CHAT_MODEL = os.getenv("OPENAI_API_MODEL", "gpt-4o-mini")
DEFAULT_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")

SYSTEM_PROMPT = (
    "Bạn là một trợ lý thiết kế thông minh, nhiệm vụ là hiểu, phân tích và hỗ trợ quy trình thiết kế sản phẩm."
)

# Hàm chính để gọi GPT với list message
def ask_gpt(messages: list[dict], model: str = DEFAULT_CHAT_MODEL, temperature: float = 0.7) -> str:
    # Đảm bảo system prompt luôn đứng đầu
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

def ask_gpt_json(messages: list[dict], model: str = DEFAULT_CHAT_MODEL, temperature: float = 0.2):
    raw = ask_gpt(messages, model=model, temperature=temperature)

    if "```" in raw:
        raw = re.sub(r"```[a-zA-Z]*\n?", "", raw).strip()
    
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, (dict, list)):
            print("[ask_gpt_json] ⚠️ Parsed JSON nhưng không phải dict/list. Type:", type(parsed))
        return parsed
    except json.JSONDecodeError as e:
        print("[ask_gpt_json] ⚠️ JSON decode failed.")
        print("[GPT Raw Output]:\n", raw)
        print("[DecodeError]", e)
        return None

# Sinh ảnh từ mô tả concept
def generate_image(prompt: str, model: str = DEFAULT_IMAGE_MODEL, size: str = "1024x1024") -> str:
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality="standard",
        n=1
    )
    return response.data[0].url
