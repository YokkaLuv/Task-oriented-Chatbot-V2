from services.openai_service import ask_gpt_json
from services.db_service import update_design_data, init_session
from schemas.design_schema import DEFAULT_DESIGN_DATA

def extract_and_store_info(phrase: str, session_id: str):
    """
    Agent B: Nhận một câu (phrase), trích xuất thông tin thiết kế, lưu vào DB.
    """

    # Prompt chuyên biệt để trích xuất thông tin thiết kế
    prompt = f"""
Bạn là AI chuyên phân tích thông tin thiết kế sản phẩm.
Hãy đọc câu sau và trích xuất các thông tin có thể dùng để thiết kế:

"{phrase}"

Yêu cầu:
- Chỉ trả về kết quả dưới dạng JSON object (không phải list)
- Các trường gợi ý: product, color, size, material, audience, style, company,...
- Nếu không có gì rõ ràng, trả về object rỗng: {{}}
- Không được giải thích, không viết thêm gì ngoài JSON.

Trả kết quả:
"""

    result = ask_gpt_json([{"role": "user", "content": prompt}], temperature=0.3)

    if not isinstance(result, dict) or not result:
        print(f"[Agent B] ⚠️ Không trích xuất được thông tin từ phrase: {phrase}")
        return

    # Lọc chỉ giữ lại các key hợp lệ theo schema
    valid_data = {}
    for key, value in result.items():
        if key in DEFAULT_DESIGN_DATA:
            valid_data[key] = value
        else:
            print(f"[Agent B] ⚠️ Field không hợp lệ: {key} → bị bỏ qua")

    if not valid_data:
        print(f"[Agent B] ⚠️ Không có field hợp lệ trong kết quả: {result}")
        return

    # Đảm bảo session tồn tại rồi mới ghi
    init_session(session_id)
    update_design_data(session_id, valid_data)
