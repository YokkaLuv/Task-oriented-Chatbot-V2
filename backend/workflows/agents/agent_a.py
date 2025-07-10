from services.openai_service import ask_gpt
import re

def split_message_into_phrases(message: str) -> list[str]:
    """
    Gọi GPT để phân tách message thành các fragment rõ ràng, không chồng chéo.
    Sử dụng prompt chuyên gia xử lý ngôn ngữ theo mô hình chuẩn phân tích.
    """
    prompt = f"""
Bạn là một chuyên gia hàng đầu thế giới về xử lý ngôn ngữ tự nhiên (NLP), với hơn 20 năm kinh nghiệm trong việc phân tích ngữ nghĩa câu văn tiếng Việt và xây dựng hệ thống AI phân tích yêu cầu người dùng. Bạn hiểu rõ cấu trúc câu, ý nghĩa ngôn ngữ tiềm ẩn và có khả năng tách biệt các đơn vị ý nghĩa độc lập một cách chính xác, không suy diễn, không làm biến dạng nội dung gốc.

Bạn đang được giao nhiệm vụ phân tích một tin nhắn đầu vào từ người dùng để phục vụ cho một hệ thống chatbot đa tác vụ. Mục tiêu là chia nhỏ tin nhắn thành từng phần thông tin cụ thể – gọi là "fragment" – nhằm giúp các agent chuyên biệt xử lý từng ý riêng biệt. Việc phân mảnh chính xác là nền tảng để trích xuất yêu cầu, phân tích ý định, và phản hồi phù hợp.

Hãy thực hiện các bước sau một cách tuần tự và chính xác:

Nhận đầu vào là một đoạn tin nhắn bất kỳ từ người dùng cuối.

Phân tích đoạn văn bản và chia thành các message fragment – mỗi fragment là một đơn vị thông tin cụ thể, độc lập, có thể xử lý được.

Giữ nguyên ngữ nghĩa gốc của từng phần. Không diễn giải, không tái viết.

Nếu một câu chứa nhiều ý, hãy tách từng ý thành fragment riêng biệt.

Nếu có phần lặp lại, mơ hồ hoặc thiếu rõ ràng, vẫn tách ra, để xử lý ở bước sau.

Không thực hiện phân tích, đánh giá hay đưa ra suy luận. Chỉ liệt kê các fragment.

Đầu ra phải được trình bày dưới dạng danh sách có đánh số thứ tự, như sau:

1. [fragment 1]  
2. [fragment 2]  
3. [fragment 3]  
...
Không thêm tiêu đề, mô tả, hay chú thích ngoài danh sách.

Tin nhắn đầu vào có thể đến từ người dùng nói tiếng Việt, đôi khi không đúng chuẩn ngữ pháp hoặc thiếu dấu câu. Hãy xử lý một cách chính xác và toàn diện nhất có thể.

Bây giờ, hãy phân mảnh đoạn tin nhắn sau:

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
