from services.openai_service import ask_gpt
from services.db_service import get_session, store_concepts, get_last_feedback
from schemas.design_schema import DEFAULT_DESIGN_DATA
import re
from json import dumps
from services.rag_service import get_context_from_session

def generate_concepts(session_id: str, num_concepts: int = 5, message: str = None) -> dict:
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
    context_from_kb = ""
    if message:
        context_from_kb = get_context_from_session(session_id, message)
        print(f"context_from_kb là {context_from_kb}")

    # ✅ Kiểm tra thiếu field (trừ 'notes')
    missing = [
        field for field in DEFAULT_DESIGN_DATA
        if field != "notes" and not design_data.get(field)
    ]
    if missing:
        print(f"[Agent D] ❌ Thiếu thông tin bắt buộc: {missing}")
        return {"error": f"Chưa đủ dữ liệu để tạo concept. Thiếu: {', '.join(missing)}."}

    # 🔍 Chuẩn bị dữ liệu
    notes = design_data.get("notes", [])
    notes_text = "".join(notes) + "." if notes else "(Không có ghi chú bổ sung)"
    design_json = dumps({k: v for k, v in design_data.items() if k != "notes"}, ensure_ascii=False, indent=2)

    # 🔁 Lấy feedback mới nhất nếu có
    last_feedback = get_last_feedback(session_id)
    feedback_text = f"\n\nLưu ý đặc biệt từ các lần đánh giá trước:\n- {last_feedback}" if last_feedback else ""

    # 🧠 Prompt
    prompt = f"""
Bạn là một chuyên gia sáng tạo hàng đầu trong lĩnh vực thiết kế thương hiệu (branding design), phát triển hệ thống nhận diện, và xây dựng hình ảnh thương hiệu cho doanh nghiệp ở nhiều ngành khác nhau. Bạn có khả năng nắm bắt nhanh bản chất thương hiệu và thể hiện nó bằng ngôn ngữ thiết kế truyền cảm hứng, sắc sảo và định hướng thị trường.

Mục tiêu:
Sinh ra {num_concepts} concept thiết kế thương hiệu khác biệt, dựa hoàn toàn vào thông tin trong `design_json` và `notes_text`. Mỗi concept phản ánh một hướng thẩm mỹ hoặc chiến lược riêng biệt.

---

Input:
- `design_json`: dữ liệu đầu vào chuẩn hóa (tên sản phẩm, màu sắc, style,...)
- `notes_text`: ghi chú của người dùng nếu có
- `context_from_kb`: dữ liệu tham khảo từ công ty mẹ của bạn
---

Yêu cầu đầu ra:
- Viết 3 đến {num_concepts} concept
- Mỗi concept là một đoạn văn sắc sảo, chi tiết và viết đầy đủ thông tin đầu vào, nếu có `notes_text`, hãy viết lại cho đẹp và ghép đầy đủ nội dung vào cuối mỗi concept
- Không được suy đoán nếu thông tin thiếu
- Có thể tham khảo theo 'context_from_kb' để sáng tạo theo 
- Phải tận dụng tối đa mọi dữ liệu có trong design_json
- Có thể dùng feedback sau để tham khảo thêm về phong cách nói: {feedback_text}
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

context_from_kb:
{context_from_kb}
"""

    response = ask_gpt([{"role": "user", "content": prompt}], temperature=0.9)

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
