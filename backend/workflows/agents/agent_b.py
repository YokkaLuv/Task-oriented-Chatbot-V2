from services.openai_service import ask_gpt_json
from services.db_service import (
    update_design_data,
    init_session,
    append_notes_to_design_data,
    remove_design_fields,
    remove_specific_field_values
)
from schemas.design_schema import DEFAULT_DESIGN_DATA

def extract_and_store_info(phrase: str, session_id: str):
    """
    Agent B: Nhận một câu (phrase), trích xuất thông tin thiết kế, lưu vào DB.
    """

    prompt = f"""
Bạn là chuyên gia trích xuất thông tin thiết về ngữ nghĩa của tiếng Việt hoạt động trong một hệ thống chatbot đa tác vụ, nhiệm vụ của bạn là trích xuất các thông tin thiết kế sản phẩm từ câu tiếng Việt và trả về kết quả dưới dạng JSON

Trích xuất càng đầy đủ càng tốt các trường sau (nếu có):

product, color, style, company, notes

Nếu thông tin không thuộc các trường trên, hãy cho vào trường "notes".

Chỉ trả về JSON object duy nhất
Ví dụ 1: 
Đầu vào: Tôi muốn thiết kế 1 cái áo thun màu trắng
Đầu ra:
{{
  "product": "áo thun",
  "color": "trắng",
}}

Ví dụ 2:
Đầu vào: Áo có in logo ở giữa 
Đầu ra:
{{
  "notes": "có in logo ở giữa",
}}

Ví dụ 3:
Đầu vào: Trang web nền trắng có thanh menu màu xanh
Đầu ra:
{{
  "product": "trang web",
  "color": "trắng",
  "notes": "có thanh menu màu xanh",
}}

Nếu không trích xuất được gì, trả về {{}}

Câu:
"{phrase}"
"""

    result = ask_gpt_json([{"role": "user", "content": prompt}], temperature=0.3)
    print(f"[Agent B Output] GPT trả về: {result}")

    if not isinstance(result, dict) or not result:
        print(f"[Agent B] ⚠️ Không trích xuất được thông tin từ phrase: {phrase}")
        return

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

            if isinstance(DEFAULT_DESIGN_DATA[key], list):
                if isinstance(value, str):
                    value_list = [v.strip() for v in value.split(",") if v.strip()]
                elif isinstance(value, list):
                    value_list = [str(v).strip() for v in value if str(v).strip()]
                else:
                    continue
                if value_list:
                    valid_data[key] = value_list
            else:
                valid_data[key] = str(value).strip()
        else:
            print(f"[Agent B] ⚠️ Field không hợp lệ: {key} → bị loại")

    init_session(session_id)

    if valid_data:
        update_design_data(session_id, valid_data)
        print(f"[Agent B] ✅ Đã cập nhật DB với: {valid_data}")

    if notes_text:
        append_notes_to_design_data(session_id, notes_text)
        print(f"[Agent B] 📝 Ghi chú bổ sung: {notes_text}")

    if not valid_data and not notes_text:
        print(f"[Agent B] ⚠️ Không có gì để lưu từ phrase: {phrase}")


def remove_info(phrase: str, session_id: str):
    """
    Agent B: Xử lý yêu cầu xoá thông tin cụ thể trong thiết kế.
    """

    prompt = f"""
Bạn là AI chuyên xử lý yêu cầu thiết kế. Hãy phân tích câu sau và trích ra các field và giá trị mà người dùng muốn xoá.

Các field hiện đang có như sau:
- products
- color
- style
- company
- notes

Yêu cầu:
- Trả về danh sách các dict dạng: [{{"field": "color", "value": "đỏ"}}, ...]
- Nếu không có giá trị cụ thể, thì chỉ cần field thôi: [{{"field": "style"}}]
- Nếu không rõ ràng, trả về []
- Chỉ trả về kết quả, không giải thích, không mở đầu, không kết luận gì thêm

Câu: "{phrase}"
"""

    result = ask_gpt_json([{"role": "user", "content": prompt}], temperature=0.2)
    print(f"[Agent B Remove] GPT trả về: {result}")

    if not isinstance(result, list) or not result:
        print(f"[Agent B Remove] ⚠️ Không xác định được thông tin cần xoá.")
        return

    fields_to_remove = []
    value_specific_removal = []

    for item in result:
        if isinstance(item, dict) and "field" in item:
            field = item["field"]
            if field not in DEFAULT_DESIGN_DATA:
                continue

            if "value" in item:
                value_specific_removal.append((field, item["value"]))
            else:
                fields_to_remove.append(field)

    if fields_to_remove:
        remove_design_fields(session_id, fields_to_remove)
        print(f"[Agent B Remove] ✅ Đã xoá toàn bộ field: {fields_to_remove}")

    for field, value in value_specific_removal:
        remove_specific_field_values(session_id, field, value)
        print(f"[Agent B Remove] ✅ Đã xoá giá trị '{value}' khỏi field '{field}'")

    return {
        "removed_fields": fields_to_remove,
        "removed_values": value_specific_removal
    }
