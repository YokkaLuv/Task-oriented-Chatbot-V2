import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load API key từ file .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DEFAULT_CHAT_MODEL = os.getenv("OPENAI_API_MODEL", "gpt-4o")
DEFAULT_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "dall-e-3")

# System prompt mặc định để giữ consistency
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

# Gọi GPT và parse kết quả về JSON (nếu dùng cho intent parser, info extractor,...)
def ask_gpt_json(messages: list[dict], model: str = DEFAULT_CHAT_MODEL, temperature: float = 0.2) -> dict | list:
    raw = ask_gpt(messages, model, temperature)
    
    try:
        return json.loads(raw)

    except json.JSONDecodeError as e:
        print("[ask_gpt_json] ⚠️ JSON decode failed.")
        print("[GPT Raw Output]:")
        print(raw)
        print("[Error]:", e)
        return []


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
