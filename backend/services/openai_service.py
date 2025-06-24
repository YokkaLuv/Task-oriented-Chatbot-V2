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
2. After those questions, keep asking client for either extra informations or generate concept. If they says no more extra informations, then asking for generate concepts only.
3. When client mention about their company name, search that on the Internet to know them better.
4. Stay on topic, be polite, warm and clear. Use Vietnamese as the agency is in Vietnam
"""

def build_message_history(user_messages):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in user_messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    return messages

def ask_gpt(messages):
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
    Generate an image using DALL·E from either full design_data or a selected concept.
    """
    if "selected_concept" in data:
        prompt = build_dalle_prompt(data["selected_concept"])
    # else:
    #     prompt = build_design_prompt(data)

    image_response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="url"
    )
    return image_response.data[0].url

