import os
from dotenv import load_dotenv
from openai import OpenAI
from services.prompt_builder import build_dalle_prompt, build_concept_generation_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a virtual assistant for a design agency. Your job is to collect design requirements from the client through a friendly and structured chat. Please follow these rules strictly:
1. Ask questions one by one to collect these requirements:
    + Business or individual? What is business name?
    + What product/service they want to design?
    + Who is the target audience?
    + Preferred color palette?
    + Desired visual style? (e.g., minimal, bold, retro...)
    + Contact information
    + Budget and timeline (optional)
2. After those questions, keep asking client for either extra informations or generate concept. If they say no more extra information, then suggest generating concepts.
3. When client mentions their company name, search that on the Internet to know them better.
4. Stay on topic, be polite, warm and clear. Use Vietnamese as the agency is in Vietnam.
"""

def ask_gpt(history: list[dict]) -> str:
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=full_messages
    )
    return response.choices[0].message.content

def extract_design_data_from_history(history: list[dict]) -> dict:
    instruction = """
Dựa trên đoạn hội thoại dưới đây giữa trợ lý và khách hàng, hãy trích xuất lại toàn bộ yêu cầu thiết kế nếu có, dưới dạng JSON với các key sau:
{
  "business": string | null,
  "product": string | null,
  "audience": string | null,
  "colors": string | null,
  "style": string | null,
  "contact_information": string | null
}
Chỉ trả về chuỗi JSON duy nhất, không thêm bất kỳ giải thích nào khác.
"""
    full_messages = [{"role": "system", "content": instruction}] + history
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=full_messages
    )
    content = response.choices[0].message.content
    try:
        import json
        return json.loads(content)
    except Exception:
        return {}

def generate_concepts_from_transcript(transcript: str) -> list[str]:
    messages = build_concept_generation_prompt(transcript)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    content = response.choices[0].message.content
    return [line.strip() for line in content.split("\n") if line.strip()]

def generate_image_from_data(data: dict) -> str:
    if "selected_concept" in data:
        prompt = build_dalle_prompt(data["selected_concept"])
    else:
        raise ValueError("No valid concept found for image generation.")
    
    image_response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="url"
    )
    return image_response.data[0].url
