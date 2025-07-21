from services.openai_service import ask_gpt
import re

def split_message_into_phrases(message: str) -> list[str]:
    """
    Gọi GPT để phân tách message thành các fragment rõ ràng, không chồng chéo.
    Sử dụng prompt chuyên gia xử lý ngôn ngữ theo mô hình chuẩn phân tích.
    """
    prompt = f"""
Bạn là một chuyên gia phân tích ngôn ngữ tiếng Việt hoạt động trong một hệ thống chatbot đa tác vụ, bạn có nhiệm vụ chia nhỏ đoạn tin nhắn của người dùng thành các đơn vị thông tin cụ thể, có liên kết, gọi là "fragment". Mỗi fragment phải:

- Là một ý riêng biệt, có thể xử lý độc lập.
- Không thêm nội dung, có thể tái diễn giải nhẹ.
- Phải giữ nguyên ý nghĩa gốc, kể cả khi thiếu chủ ngữ hoặc dấu câu.
- Trường hợp văn bản mơ hồ hoặc không hoàn chỉnh, vẫn phải giữ lại.
- Lưu ý với các câu dài khi fragment này có liên kết với fragment kia, hãy kết hợp nó thành một.

---

**Đầu vào:**

Một đoạn tin nhắn tiếng Việt của người dùng. Ví dụ:

> "Tôi muốn thiết kế logo cho shop mỹ phẩm, làm thêm banner nếu được. Banner có màu nâu nhạt. Tạo ý tưởng và demo cho tôi đi."

---

**Đầu ra mong muốn (dạng danh sách):**

1. Tôi muốn thiết kế logo cho shop mỹ phẩm  
2. Làm thêm banner nếu được. Banner có màu nâu nhạt.
3. Tạo ý tưởng
4. Tạo demo cho tôi đi

---

Bây giờ, hãy phân mảnh đoạn tin nhắn sau:

"{message}"

Trả lời chỉ với danh sách fragment. Không thêm mô tả, không giải thích, không kết luận.

"""

    raw_output = ask_gpt([{"role": "user", "content": prompt}], temperature=0.3)

    # Parse từng dòng dạng "1. nội dung"
    fragments = []
    for line in raw_output.splitlines():
        match = re.match(r"^\s*\d+\.\s+(.*)", line.strip())
        if match:
            fragments.append(match.group(1).strip())

    return fragments
