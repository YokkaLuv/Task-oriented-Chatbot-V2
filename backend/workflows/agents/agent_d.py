from services.openai_service import ask_gpt
from services.db_service import get_session, store_concepts
from schemas.design_schema import DEFAULT_DESIGN_DATA
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

    # ✅ Kiểm tra thiếu field (trừ 'notes')
    missing = [
        field for field in DEFAULT_DESIGN_DATA
        if field != "notes" and not design_data.get(field)
    ]

    if missing:
        print(f"[Agent D] ❌ Thiếu thông tin bắt buộc: {missing}")
        return {"error": f"Chưa đủ dữ liệu để tạo concept. Thiếu: {', '.join(missing)}."}

    # Chuẩn bị dữ liệu
    notes = design_data.get("notes", [])
    # Cho phép liệt kê với gợi tả nhẹ
    notes_text = "".join(notes) + "." if notes else "(Không có ghi chú bổ sung)"
    print(notes_text)

    design_json = dumps({k: v for k, v in design_data.items() if k != "notes"}, ensure_ascii=False, indent=2)

    prompt = f"""
Bạn là một chuyên gia sáng tạo hàng đầu trong lĩnh vực thiết kế thương hiệu (branding design), phát triển hệ thống nhận diện, và xây dựng hình ảnh thương hiệu cho doanh nghiệp ở nhiều ngành khác nhau. Bạn có khả năng nắm bắt nhanh bản chất thương hiệu và thể hiện nó bằng ngôn ngữ thiết kế truyền cảm hứng, sắc sảo và định hướng thị trường

Mục tiêu:
Sinh ra {num_concepts} concept thiết kế thương hiệu khác biệt, dựa hoàn toàn vào thông tin trong `design_json` và `notes_text`. Mỗi concept phản ánh một hướng thẩm mỹ hoặc chiến lược riêng biệt.

---

Input:
- `design_json`: dữ liệu đầu vào chuẩn hóa (tên sản phẩm, màu sắc, style,...)
- `notes_text`: ghi chú của người dùng nếu có

---

Yêu cầu đầu ra:
- Viết 3 đến {num_concepts} concept
- Mỗi concept là một đoạn văn ngắn gọn, sắc sảo, chi tiết và viết đầy đủ thông tin đầu vào, nếu có `notes_text`, hãy viết lại cho đẹp và ghép đầy đủ nội dung vào cuối mỗi concept
- Không được suy đoán nếu thông tin thiếu
- Phải tận dụng tối đa mọi dữ liệu có trong design_json
- Không giới thiệu, không phân tích, chỉ in ra danh sách như mẫu dưới đây

---

Output format:
1. [Ý tưởng 1]
2. [Ý tưởng 2]
3. ...

Không dùng markdown, không xuống dòng. Không có tiêu đề hay giải thích gì khác.

---

Dữ liệu đầu vào:

design_json:
{design_json}

notes_text:
{notes_text}

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
        concepts = [p.strip() for p in response.split("\n\n") if p.strip()]

    if concepts:
        store_concepts(session_id, concepts)
        return {"concepts": concepts}
    else:
        print(f"[Agent D] ❌ GPT không trả về concept hợp lệ.")
        return {"error": "Không thể tạo concept từ dữ liệu hiện tại."}
