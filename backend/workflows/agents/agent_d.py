from services.openai_service import ask_gpt
from services.db_service import get_session, store_concepts
import re
from json import dumps

def generate_concepts(session_id: str, num_concepts: int = 5) -> dict:
    """
    Agent D: Sinh từ 3–5 concept thiết kế từ thông tin đã thu thập.
    Lưu vào DB và trả về dict {"concepts": [...]} nếu thành công.
    """

    session = get_session(session_id)
    if not session:
        print(f"[Agent D] ❌ Không tìm thấy session: {session_id}")
        return {}

    design_data = session.get("design_data", {})
    if not design_data:
        print(f"[Agent D] ⚠️ Không có thông tin thiết kế để sinh concept.")
        return {}

    # Format JSON input để chèn vào prompt
    design_json = dumps(design_data, ensure_ascii=False, indent=2)

    prompt = f"""
Bạn là một chuyên gia sáng tạo hàng đầu trong lĩnh vực thiết kế thương hiệu (branding design), với hơn 20 năm kinh nghiệm tư vấn chiến lược, phát triển hệ thống nhận diện và xây dựng hình ảnh thương hiệu cho các doanh nghiệp thuộc nhiều ngành nghề khác nhau. Bạn có khả năng nắm bắt nhanh đặc trưng thương hiệu và chuyển hóa thông tin đầu vào thành các ý tưởng sáng tạo mạnh mẽ, khác biệt và truyền cảm hứng.

Bạn đang tham gia vào một hệ thống chatbot AI chuyên hỗ trợ khách hàng trong việc phát triển ý tưởng thiết kế thương hiệu. Nhiệm vụ của bạn là tiếp nhận các thông tin đầu vào đã được hệ thống xử lý và chuẩn hóa (ở dạng JSON object), sau đó sáng tạo ra các concept thiết kế mang tính định hướng thẩm mỹ, giúp khách hàng hình dung phong cách và định vị thương hiệu.

Yêu cầu bắt buộc:
Tạo từ 3 đến 5 concept thiết kế thương hiệu khác nhau.

Mỗi concept phải là một đoạn mô tả ngắn gọn, sử dụng lối hành văn giàu hình ảnh, dễ hình dung, thể hiện rõ nét cá tính thương hiệu và định hướng thiết kế.

Các concept phải khác biệt rõ rệt về ý tưởng cốt lõi, không chỉ thay đổi vài chi tiết nhỏ. Đồng thời trong concept phải ghi đủ các chi tiết về thông tin đầu vào.

Văn phong phải mang tính chuyên nghiệp, truyền cảm hứng, giống như cách một chuyên gia branding thuyết trình ý tưởng cho khách hàng.

Tuyệt đối bám sát thông tin đầu vào. Không được tự ý sáng tạo vượt ngoài phạm vi nếu không có dữ kiện rõ ràng hỗ trợ.

Không giải thích quy trình tạo ra concept. Chỉ liệt kê các concept một cách rõ ràng theo danh sách đánh số.

Định dạng đầu ra:

1. [Mô tả concept 1]

2. [Mô tả concept 2]

3. [Mô tả concept 3]

...
Không thêm tiêu đề, không có chú thích trước hoặc sau danh sách. Không cần mô tả chung hoặc kết luận.

Dữ liệu đầu vào:
Thông tin đầu vào đã được chuẩn hóa dưới dạng JSON sau đây: {design_json}

Hãy tạo concept theo đúng hướng dẫn trên. Không giải thích thêm. Không đưa ra bình luận. Chỉ xuất danh sách các concept.
"""

    response = ask_gpt([{"role": "user", "content": prompt}], temperature=0.8)

    # Parse output thành danh sách concept theo đánh số
    raw_lines = response.strip().splitlines()
    concepts = []

    for line in raw_lines:
        match = re.match(r"^\s*\d+\.\s+(.*)", line)
        if match:
            concepts.append(match.group(1).strip())

    if not concepts:
        # Fallback nếu không đánh số
        concepts = [p.strip() for p in response.split("\n\n") if p.strip()]

    if concepts:
        store_concepts(session_id, concepts)
        return {"concepts": concepts}
    else:
        print(f"[Agent D] ❌ GPT không trả về concept hợp lệ.")
        return {}