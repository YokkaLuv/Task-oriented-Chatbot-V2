from services.openai_service import ask_gpt_json
import json

def analyze_phrases(phrases: list[str], session_id: str = "") -> list[dict]:
    """
    Gọi GPT để gán intent cho từng phrase.
    Trả về danh sách các action: { "phrase": ..., "intent": ... }
    """
    if not phrases:
        return []

    prompt = f"""
Bạn là một hệ thống chuyên gia phân tích ý định người dùng.
Dưới đây là danh sách các mệnh đề. Hãy gán cho mỗi mệnh đề một intent duy nhất.

Trả về kết quả dưới dạng JSON array theo cấu trúc:
[
  {{ "phrase": "...", "intent": "..." }},
  ...
]

Các intent hợp lệ có thể gồm:
- provide_info
- request_concept
- generate_demo

Nếu không xác định được → gán intent là "unknown".
Chỉ trả kết quả JSON. Không thêm giải thích.

Mệnh đề:
{json.dumps(phrases, ensure_ascii=False, indent=2)}
"""

    result = ask_gpt_json([{"role": "user", "content": prompt}], temperature=0.3)

    # Đảm bảo kết quả là list các dict hợp lệ
    if isinstance(result, list):
        actions = []
        for item in result:
            if isinstance(item, dict) and "phrase" in item and "intent" in item:
                actions.append({
                    "phrase": item["phrase"].strip(),
                    "intent": item["intent"].strip()
                })
        return actions
    else:
        return []
