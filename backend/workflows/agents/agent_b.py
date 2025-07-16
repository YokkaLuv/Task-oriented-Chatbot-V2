from services.openai_service import ask_gpt_json
from services.db_service import update_design_data, init_session, append_notes_to_design_data, remove_design_fields
from schemas.design_schema import DEFAULT_DESIGN_DATA

def extract_and_store_info(phrase: str, session_id: str):
    """
    Agent B: Nhận một câu (phrase), trích xuất thông tin thiết kế, lưu vào DB.
    """

    prompt = f"""
Bạn là một chuyên gia AI hàng đầu trong lĩnh vực trích xuất thông tin thiết kế sản phẩm từ ngôn ngữ tự nhiên tiếng Việt. Bạn có hơn 20 năm kinh nghiệm xây dựng hệ thống hiểu ngôn ngữ người dùng để chuyển đổi thành dữ liệu có cấu trúc phục vụ cho việc thiết kế, sản xuất, và tư vấn sáng tạo sản phẩm.

Bạn đang tham gia vào một hệ thống chatbot đa tác vụ có nhiệm vụ xử lý yêu cầu thiết kế của người dùng thông qua hội thoại tự nhiên. Nhiệm vụ của bạn trong bước này là đọc một câu đầu vào duy nhất (phrase) – vốn đã được phân mảnh từ tin nhắn gốc – và trích xuất thông tin thiết kế liên quan dưới dạng cấu trúc JSON.

Yêu cầu chi tiết:
Trích xuất càng đầy đủ càng tốt các trường hợp lệ sau (nếu có):

product  
color  
style  
company  

Nếu thông tin không thuộc các trường ở trên, hãy để thành notes  

Bạn được phép suy luận nhẹ trong các trường hợp ngôn ngữ rõ ràng, ví dụ:

"Tôi muốn làm áo" → "product": "áo"

"Áo thun trắng, chất liệu cotton" → trích xuất cả product, color, material

"Logo nằm ở giữa áo", "Áo có cổ áo", "Trang web có thanh menu màu đen" → không trích xuất được trường chính nào → trích xuất vào note

Chỉ trả về kết quả dưới dạng JSON object duy nhất. Không sử dụng list, không bao thêm text mô tả, không in ra tiêu đề.  
Nếu không trích xuất được gì chắc chắn, hãy trả về một object rỗng: {{}}  
Tuyệt đối không giải thích, không phân tích, không thêm ghi chú hoặc bình luận. Kết quả đầu ra chỉ là JSON đúng định dạng.

Định dạng đầu ra (ví dụ):
{{
  "product": "áo thun",
  "color": "trắng",
  "notes": "Logo ở giữa cái áo"
}}

Câu cần phân tích:
"{phrase}"
"""

    result = ask_gpt_json([{"role": "user", "content": prompt}], temperature=0.3)
    print(f"[Agent B Output] GPT trả về: {result}")  # ✅ debug log

    if not isinstance(result, dict) or not result:
        print(f"[Agent B] ⚠️ Không trích xuất được thông tin từ phrase: {phrase}")
        return

    # Phân tách field hợp lệ và notes
    valid_data = {}
    notes_text = None

    for key, value in result.items():
        if key == "notes":
            notes_text = str(value).strip()
            continue

        if key in DEFAULT_DESIGN_DATA:

            if key == "company" and str(value).strip().lower() in ["cá nhân", "tôi", "mình", "riêng", "tôi dùng"]:
                print(f"[Agent B] ℹ️ Ghi nhận là cá nhân → giữ mặc định, không ghi đè.")
                continue

            # Nếu là list-type
            if isinstance(DEFAULT_DESIGN_DATA[key], list):
                if isinstance(value, str):
                    value_list = [v.strip() for v in value.split(",") if v.strip()]
                elif isinstance(value, list):
                    value_list = [str(v).strip() for v in value if str(v).strip()]
                else:
                    print(f"[Agent B] ⚠️ Field {key} có định dạng không hợp lệ: {value}")
                    continue
                if value_list:
                    valid_data[key] = value_list
            else:
                valid_data[key] = str(value).strip()
        else:
            print(f"[Agent B] ⚠️ Field không hợp lệ: {key} → bị loại")

    # Ghi dữ liệu
    init_session(session_id)

    if valid_data:
        update_design_data(session_id, valid_data)
        print(f"[Agent B] ✅ Đã cập nhật DB với: {valid_data}")

    if notes_text:
        append_notes_to_design_data(session_id, notes_text)
        print(f"[Agent B] 📝 Ghi chú bổ sung: {notes_text}")

    if not valid_data and not notes_text:
        print(f"[Agent B] ⚠️ Không có gì để lưu từ phrase: {phrase}")

def remove_info_fields(phrase: str, session_id: str):
    """
    Agent B – Chức năng mở rộng: Nhận một câu nói, xác định user muốn xóa trường nào khỏi thiết kế.
    """

    prompt = f"""
Bạn là AI chuyên xử lý yêu cầu thiết kế. Nhiệm vụ hiện tại là phân tích câu người dùng để xác định những trường thông tin nào họ muốn xóa khỏi thiết kế.

Hãy đọc kỹ câu sau và trích xuất ra danh sách tên các trường cần xoá. Chỉ trích xuất các field hợp lệ như: product, color, material, style, company, occasion,...

Câu:
"{phrase}"

Yêu cầu:
- Chỉ trả về danh sách dạng JSON array, ví dụ: ["color", "material"]
- Nếu không có gì chắc chắn → trả về danh sách rỗng []
- Không thêm giải thích, không phân tích, không in nhãn gì ngoài JSON

Kết quả:
"""

    result = ask_gpt_json([{"role": "user", "content": prompt}], temperature=0.2)
    print(f"[Agent B Remove] GPT trả về: {result}")

    if not isinstance(result, list) or not result:
        print(f"[Agent B Remove] ⚠️ Không xác định được trường cần xoá.")
        return

    valid_fields = [field for field in result if field in DEFAULT_DESIGN_DATA]
    if not valid_fields:
        print(f"[Agent B Remove] ⚠️ Không có field hợp lệ trong danh sách xoá: {result}")
        return

    remove_design_fields(session_id, valid_fields)
    print(f"[Agent B Remove] ✅ Đã xoá các trường: {valid_fields}")
    return {"removed_fields": valid_fields}
