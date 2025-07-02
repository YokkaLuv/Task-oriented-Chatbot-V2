from backend.services.openai_service import ask_gpt_json
from backend.services.db_service import update_design_data, init_session

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
- Các trường gợi ý: product, color, size, material, audience, style, shape,...
- Nếu không có gì rõ ràng, trả về object rỗng: {{}}
- Không được giải thích, không viết thêm gì ngoài JSON.

Trả kết quả:
"""

    result = ask_gpt_json([{"role": "user", "content": prompt}], temperature=0.3)

    # Nếu kết quả là dict hợp lệ, lưu vào DB
    if isinstance(result, dict) and result:
        # Đảm bảo session tồn tại trước
        init_session(session_id)
        update_design_data(session_id, result)
    else:
        print(f"[Agent B] ⚠️ Không trích xuất được thông tin từ phrase: {phrase}")
