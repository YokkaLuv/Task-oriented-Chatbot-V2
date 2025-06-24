# def build_design_prompt(data: dict) -> str:
#     """
#     Build a prompt string for GPT or DALL·E based on structured user data.
#     Expected keys: business, product, audience, colors, style, budget, timeline, company_name (optional)
#     """
#     prompt = f"""
# Create a creative visual design concept based on the following details:

# - Business or Individual: {data.get('business', 'N/A')}
# - Company/Product/Service: {data.get('product', 'N/A')}
# - Target Audience: {data.get('audience', 'N/A')}
# - Color Preferences: {data.get('colors', 'N/A')}
# - Visual Style: {data.get('style', 'N/A')}
# - Budget: {data.get('budget', 'N/A')}
# - Timeline: {data.get('timeline', 'N/A')}
# - Company Name (if any): {data.get('company_name', 'N/A')}

# The output should be a short, visually inspiring design direction or concept idea suitable for quick illustration or image generation.
#     """
#     return prompt.strip()

def build_concept_generation_prompt(transcript: str) -> list:
    """
    Tạo prompt cho GPT để sinh 3 concept thiết kế dựa trên đoạn hội thoại giữa khách hàng và AI.
    Trả về danh sách message để dùng trong Chat API.
    """
    system = {
        "role": "system",
        "content": """
You are a creative brand designer. Your job is to create 3 distinct design concepts for a client based on their requirements.
Read the full conversation below between a client and a design assistant, then generate the concepts.

Each concept should be:
- 1 short paragraph (~3-4 sentences)
- Unique in theme and visual direction
- Based on the client's preferences and use-case

Respond only with the 3 concepts as plain text. Number them like "Concept 1: ...", "Concept 2: ...", etc.
"""
    }

    user = {
        "role": "user",
        "content": f"Conversation:\n{transcript}"
    }

    return [system, user]

def build_dalle_prompt(concept: str) -> str:
    """
    Build a visual prompt for DALL·E based on a selected concept string.
    """
    return f"""
Generate a creative visual design based on the following concept:
"{concept}"

The image should reflect the described theme, style, and color direction.
Avoid any text in the image. Return only a single visual illustration.
""".strip()
