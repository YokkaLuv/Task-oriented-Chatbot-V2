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

def build_message_history(history: list[dict], user_message: str) -> list[dict]:
    return [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_message}]

def ask_gpt(messages: list[dict]) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=messages
    )
    return response.choices[0].message.content

def generate_concepts_from_transcript(transcript: str) -> list[str]:
    messages = build_concept_generation_prompt(transcript)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    content = response.choices[0].message.content
    concepts = [line.strip() for line in content.split("\n") if line.strip()]
    return concepts

def generate_image_from_data(data: dict) -> str:
    """
    Generate an image using DALL·E from either a full data dict or a selected concept string.
    """
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
