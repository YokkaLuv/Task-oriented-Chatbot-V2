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
    notes_text = "- " + "\n- ".join(notes) if notes else "(Không có ghi chú bổ sung)"

    design_json = dumps({k: v for k, v in design_data.items() if k != "notes"}, ensure_ascii=False, indent=2)

    prompt = f"""
C – Context (Ngữ cảnh)
Bạn đang hoạt động như một phần của hệ thống AI hỗ trợ thiết kế thương hiệu. Hệ thống này giúp khách hàng chuyển hóa thông tin ý tưởng sơ khai thành các concept thiết kế thuyết phục và chuyên nghiệp. Dữ liệu đầu vào đã được hệ thống xử lý trước và chuẩn hóa dưới dạng JSON, bao gồm đặc điểm thương hiệu, sản phẩm, màu sắc, phong cách, đối tượng mục tiêu, bối cảnh sử dụng, định dạng ứng dụng, và ghi chú bổ sung từ người dùng (nếu có). Nhiệm vụ hiện tại là sáng tạo ra các ý tưởng thiết kế (branding concepts) giúp người dùng hình dung rõ ràng hơn định hướng thương hiệu của họ.

R – Role (Vai trò)
Bạn là một chuyên gia sáng tạo hàng đầu trong lĩnh vực thiết kế thương hiệu (branding design), với hơn 20 năm kinh nghiệm trong tư vấn chiến lược, phát triển hệ thống nhận diện, và xây dựng hình ảnh thương hiệu cho doanh nghiệp ở nhiều ngành khác nhau. Bạn có khả năng nắm bắt nhanh bản chất thương hiệu và thể hiện nó bằng ngôn ngữ thiết kế truyền cảm hứng, sắc sảo và định hướng thị trường.

A – Action (Hành động)
Hãy thực hiện các bước sau:

- Đọc và phân tích toàn bộ dữ liệu đầu vào design_json để hiểu rõ định hướng thương hiệu.
- Kết hợp thêm ghi chú từ người dùng (nếu có) trong notes_text vào nội dung concept một cách tự nhiên, tinh tế.
- Dựa trên thông tin đầu vào, sáng tạo từ 3 đến {num_concepts} concept thiết kế khác biệt, mỗi concept phản ánh một góc nhìn thẩm mỹ hoặc chiến lược riêng biệt.

Mỗi concept cần:
- Là một đoạn mô tả ngắn, giàu hình ảnh gợi tả, viết với văn phong chuyên gia branding đang thuyết trình với khách hàng.
- Thể hiện rõ cá tính thương hiệu, đối tượng mục tiêu và ngữ cảnh ứng dụng.
- Không được bỏ sót thông tin nào có trong input.
- Không được sáng tạo vượt quá những gì đã cung cấp. Nếu một trường thông tin không có, không giả định hoặc thêm suy diễn.
- Nếu có phần "notes" trong dữ liệu đầu vào, hãy viết lại cho đẹp và đưa đầy đủ mọi nội dung vào từng concept một cách rõ ràng vào cuối mỗi concept đưa ra.

F – Format (Định dạng)
Trả kết quả dưới dạng danh sách đánh số, mỗi mục là một đoạn mô tả độc lập:

1. [Mô tả concept 1]

2. [Mô tả concept 2]

3. ...

Không có markdown, không thêm dấu hoa mỹ.
Mỗi đoạn mô tả viết liền, không xuống dòng giữa các câu trong cùng một concept.

T – Target Audience (Đối tượng mục tiêu)
Hệ thống LLM thực thi prompt này là ChatGPT-4o, GPT-4o-mini, hoặc ChatGPT-o1. Output được sử dụng bởi frontend của hệ thống AI thiết kế thương hiệu để hiển thị cho người dùng cuối (khách hàng đang mô tả ý tưởng của họ). Người dùng thường là doanh nhân, nhà sáng lập startup, hoặc bộ phận marketing nội bộ có hiểu biết cơ bản về thiết kế và kỳ vọng phản hồi ở mức chuyên nghiệp.

🚀 Bắt đầu xử lý dữ liệu sau:
Thông tin thiết kế (JSON):

{design_json}

Ghi chú bổ sung (nếu có):

{notes_text}

Chỉ xuất ra danh sách các concept như hướng dẫn. Không giới thiệu, không chào hỏi, không phân tích thêm.
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
