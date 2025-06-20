def build_design_prompt(data: dict) -> str:
    """
    Build a prompt string for GPT or DALL·E based on structured user data.
    Expected keys: business, product, audience, colors, style, budget, timeline, company_name (optional)
    """
    prompt = f"""
Create a creative visual design concept based on the following details:

- Business or Individual: {data.get('business', 'N/A')}
- Company/Product/Service: {data.get('product', 'N/A')}
- Target Audience: {data.get('audience', 'N/A')}
- Color Preferences: {data.get('colors', 'N/A')}
- Visual Style: {data.get('style', 'N/A')}
- Budget: {data.get('budget', 'N/A')}
- Timeline: {data.get('timeline', 'N/A')}
- Company Name (if any): {data.get('company_name', 'N/A')}

The output should be a short, visually inspiring design direction or concept idea suitable for quick illustration or image generation.
    """
    return prompt.strip()
