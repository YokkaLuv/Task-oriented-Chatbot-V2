from services.openai_service import ask_gpt_json
from services.db_service import update_design_data, init_session
from schemas.design_schema import DEFAULT_DESIGN_DATA

def extract_and_store_info(phrase: str, session_id: str):
    """
    Agent B: Nhận một câu (phrase), trích xuất thông tin thiết kế, lưu vào DB.
    """

    prompt = f"""
Bạn là một AI chuyên phân tích thông tin thiết kế sản phẩm từ ngôn ngữ tự nhiên.
Hãy đọc câu sau và trích xuất các thông tin liên quan đến thiết kế. Bạn được phép **suy luận nhẹ** nếu thông tin quá rõ ràng (ví dụ: "tôi muốn làm áo" → product = "áo").

Câu:
"{phrase}"

Chỉ trả về kết quả dưới dạng JSON object, ví dụ:
{{
  "product": "áo thun",
  "color": "trắng",
  "material": "vải cotton",
  ...
}}

Các trường hợp lệ: product, color, size, material, audience, style, company, occasion,...

Yêu cầu bắt buộc:
- Chỉ trả JSON object (không phải list)
- Không giải thích, không mô tả thêm
- Nếu không có gì chắc chắn, trả về {{}}
"""

    result = ask_gpt_json([{"role": "user", "content": prompt}], temperature=0.3)
    print(f"[Agent B Output] GPT trả về: {result}")  # ✅ debug log

    if not isinstance(result, dict) or not result:
        print(f"[Agent B] ⚠️ Không trích xuất được thông tin từ phrase: {phrase}")
        return

    # Lọc field hợp lệ
    valid_data = {}
    for key, value in result.items():
        if key in DEFAULT_DESIGN_DATA:
            valid_data[key] = value
        else:
            print(f"[Agent B] ⚠️ Field không hợp lệ: {key} → bị loại")

    if not valid_data:
        print(f"[Agent B] ⚠️ Không có field hợp lệ trong kết quả: {result}")
        return

    # Đảm bảo session tồn tại
    init_session(session_id)
    update_design_data(session_id, valid_data)
    print(f"[Agent B] ✅ Đã cập nhật DB với: {valid_data}")
