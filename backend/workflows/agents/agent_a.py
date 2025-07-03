from services.openai_service import ask_gpt
import re

def split_message_into_phrases(message: str) -> list[str]:
    """
    Gọi GPT để phân tách message thành các fragment rõ ràng, không chồng chéo.
    Sử dụng prompt chuyên gia xử lý ngôn ngữ theo mô hình chuẩn phân tích.
    """
    prompt = f"""
Bạn là một AI chuyên gia xử lý ngôn ngữ, có nhiệm vụ phân tích một tin nhắn đầu vào thành các mảnh thông tin đơn lẻ, còn gọi là message fragment. Mỗi fragment phải thể hiện một ý cụ thể, không chồng chéo, không mơ hồ, không bị trộn với các ý khác.

Yêu cầu:
1. Mỗi fragment là một câu đơn hoặc một mệnh đề độc lập chứa thông tin có thể phân tích được.
2. Không được bỏ sót các chi tiết nhỏ. Nếu người dùng dùng một cụm từ dài có chứa nhiều ý, cần tách riêng từng ý.
3. Không sửa nội dung fragment, giữ nguyên ngữ nghĩa gốc (chỉ tách, không diễn giải).
4. Nếu có thông tin lặp lại hoặc không rõ ràng, vẫn phải tách ra riêng để xử lý sau.
5. Không phân tích hay đánh giá các fragment – chỉ liệt kê.

Đầu ra phải là một danh sách các fragment, đánh số thứ tự như sau:
1. ...
2. ...
3. ...

**Bây giờ, hãy phân mảnh tin nhắn sau:**

\"{message}\"
"""

    raw_output = ask_gpt([{"role": "user", "content": prompt}], temperature=0.3)

    # Parse từng dòng dạng "1. nội dung"
    fragments = []
    for line in raw_output.splitlines():
        match = re.match(r"^\s*\d+\.\s+(.*)", line.strip())
        if match:
            fragments.append(match.group(1).strip())

    return fragments
