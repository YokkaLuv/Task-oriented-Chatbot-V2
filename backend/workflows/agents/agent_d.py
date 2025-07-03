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
Bạn là một chuyên gia sáng tạo trong lĩnh vực thiết kế thương hiệu. Nhiệm vụ của bạn là tạo ra các ý tưởng thiết kế (concept) sáng tạo, độc đáo, phù hợp với thông tin yêu cầu từ khách hàng.

Thông tin được cung cấp gồm các đặc điểm về thương hiệu, mục tiêu, tệp khách hàng, màu sắc, phong cách, định dạng ứng dụng, và các yêu cầu đặc biệt khác.

Yêu cầu:

1. Đưa ra từ 3 đến 5 concept khác nhau, mỗi concept là một đoạn mô tả ngắn gọn, giàu hình ảnh, dễ hình dung, thể hiện được cá tính thương hiệu và định hướng thiết kế.
2. Mỗi concept phải khác biệt rõ ràng về ý tưởng cốt lõi, không được chỉ thay đổi chi tiết nhỏ.
3. Bám sát các thông tin đã cho – không được sáng tạo vượt ngoài yêu cầu nếu không có lý do rõ ràng.
4. Dùng văn phong chuyên nghiệp, truyền cảm hứng, như cách một chuyên gia branding thuyết trình ý tưởng.
5. Output phải là danh sách đánh số rõ ràng.

**Thông tin yêu cầu thiết kế:**
{design_json}

Hãy tạo concept theo đúng hướng dẫn trên. Không giải thích thêm.
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