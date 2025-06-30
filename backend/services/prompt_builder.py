import re
from typing import Optional

def build_concept_generation_prompt(transcript: str) -> list[dict]:
    """
    Tạo prompt cho GPT để sinh 3 concept thiết kế dựa trên đoạn hội thoại giữa khách hàng và AI.
    Trả về danh sách message để dùng trực tiếp với OpenAI Chat API.

    transcript: đoạn hội thoại định dạng text (role: message)
    """
    system_msg = {
        "role": "system",
        "content": """
You are a creative brand designer. Your job is to create 3 distinct design concepts for a client based on their requirements.
Read the full conversation below between a client and a design assistant, then generate the concepts.

Each concept should be:
- 1 short paragraph (~3-4 sentences)
- Unique in theme and visual direction
- Based on the client's preferences and use-case

Respond only with the 3 concepts as plain text. Number them like "Ý tưởng 1: ...", "Ý tưởng 2: ...", etc.
""".strip()
    }

    user_msg = {
        "role": "user",
        "content": f"Conversation:\n{transcript}"
    }

    return [system_msg, user_msg]


def build_dalle_prompt(concept: str) -> str:
    """
    Sinh prompt cho DALL·E từ concept văn bản được chọn.
    
    concept: văn bản mô tả concept thiết kế do GPT đề xuất.
    """
    return f"""
Generate a creative visual design based on the following concept:
"{concept}"

The image should reflect the described theme, style, and color direction.
""".strip()


def extract_selected_concept_index(message: str, concepts: list[str]) -> Optional[int]:
    """
    Phân tích message của người dùng để xác định họ chọn concept số mấy, hoặc concept nào trùng tên.

    Ưu tiên:
    1. Câu chứa số thứ tự (VD: “Tôi chọn số 2”)
    2. Tên concept (VD: “Tôi thích concept Bold Clean”)
    3. Cách nói phổ biến như “tôi thích 1”, “ý 2”, “chọn số 3” v.v.
    """
    message = message.lower().strip()

    # ✅ Regex: "ý tưởng", "concept", "số", "ý", v.v.
    match = re.search(r"(?:ý\s*tưởng|concept|số|ý)?\s*(\d+)", message)
    if match:
        idx = int(match.group(1)) - 1
        if 0 <= idx < len(concepts):
            return idx

    # ✅ Một số cụm từ thường gặp không cần regex
    for i in range(len(concepts)):
        if (
            f"chọn {i+1}" in message
            or f"tôi chọn {i+1}" in message
            or f"mình chọn {i+1}" in message
            or f"ý {i+1}" in message
            or f"thích {i+1}" in message
        ):
            return i

    # ✅ Nếu tên concept có trong message
    for i, concept in enumerate(concepts):
        if concept.lower() in message:
            return i

    return None