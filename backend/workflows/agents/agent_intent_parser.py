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

Các intent hợp lệ gồm:
- provide_info         → khi người dùng cung cấp thông tin chi tiết cho thiết kế (màu sắc, chất liệu, đối tượng,...)
- request_concept      → khi người dùng yêu cầu bạn đưa ra các concept thiết kế dựa trên thông tin hiện có
- choose_concept       → khi người dùng chọn một concept cụ thể từ danh sách đã gợi ý
- generate_demo        → khi người dùng yêu cầu tạo hình ảnh demo minh hoạ từ concept đã chọn
- unknown              → nếu không xác định được ý định

Lưu ý:
- Nếu người dùng nói "Tôi chọn concept Xanh Biển Sâu" → intent là "choose_concept"
- Nếu người dùng nói "Hãy tạo hình ảnh cho thiết kế của tôi" → intent là "generate_demo"
- Nếu người dùng mô tả sản phẩm (tên sản phẩm, màu sắc, chất liệu, đối tượng, mục đích...) → intent là "provide_info"
- Nếu người dùng yêu cầu bạn đề xuất ý tưởng thiết kế → intent là "request_concept"

Chỉ trả kết quả JSON hợp lệ, không được giải thích gì thêm.

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
