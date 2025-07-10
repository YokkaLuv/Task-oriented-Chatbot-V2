from services.openai_service import ask_gpt_json
from services.db_service import update_design_data, init_session
from schemas.design_schema import DEFAULT_DESIGN_DATA

def extract_and_store_info(phrase: str, session_id: str):
    """
    Agent B: Nhận một câu (phrase), trích xuất thông tin thiết kế, lưu vào DB.
    """

    prompt = f"""
Bạn là một chuyên gia AI hàng đầu trong lĩnh vực trích xuất thông tin thiết kế sản phẩm từ ngôn ngữ tự nhiên tiếng Việt. Bạn có hơn 20 năm kinh nghiệm xây dựng hệ thống hiểu ngôn ngữ người dùng để chuyển đổi thành dữ liệu có cấu trúc phục vụ cho việc thiết kế, sản xuất, và tư vấn sáng tạo sản phẩm.

Bạn đang tham gia vào một hệ thống chatbot đa tác vụ có nhiệm vụ xử lý yêu cầu thiết kế của người dùng thông qua hội thoại tự nhiên. Nhiệm vụ của bạn trong bước này là đọc một câu đầu vào duy nhất (phrase) – vốn đã được phân mảnh từ tin nhắn gốc – và trích xuất thông tin thiết kế liên quan dưới dạng cấu trúc JSON.

Bạn được phép suy luận nhẹ trong các trường hợp ngôn ngữ rõ ràng, ví dụ:

"Tôi muốn làm áo" → "product": "áo"

"Áo thun trắng, chất liệu cotton" → trích xuất cả product, color, material
Tuy nhiên, không được suy diễn quá mức. Nếu thông tin không rõ ràng, không chắc chắn hoặc mơ hồ, hãy bỏ qua và không đưa vào JSON.

Yêu cầu chi tiết:
Trích xuất càng đầy đủ càng tốt các trường hợp lệ sau (nếu có):

product

color

size

material

style

company

occasion

... (các trường khác nếu có thể hợp lý hóa từ ngữ cảnh)

Chỉ trả về kết quả dưới dạng JSON object duy nhất. Không sử dụng list, không bao thêm text mô tả, không in ra tiêu đề.

Nếu không trích xuất được gì chắc chắn, hãy trả về một object rỗng: {{}}

Tuyệt đối không giải thích, không phân tích, không thêm ghi chú hoặc bình luận. Kết quả đầu ra chỉ là JSON đúng định dạng.

Định dạng đầu ra (ví dụ):
{{
  "product": "áo thun",
  "color": "trắng",
  "material": "vải cotton"
}}

Câu cần phân tích:
"{phrase}"
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
            # Nếu key là "company" nhưng user nói là cá nhân → bỏ qua để giữ default
            if key == "company" and str(value).strip().lower() in ["cá nhân", "tôi", "mình", "riêng", "tôi dùng"]:
                print(f"[Agent B] ℹ️ Ghi nhận là cá nhân → giữ mặc định, không ghi đè.")
                continue
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
