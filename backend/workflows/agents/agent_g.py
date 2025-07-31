from services.openai_service import ask_gpt
from services.db_service import get_session
from json import dumps
from services.rag_service import get_context_from_session

def generate_dalle_prompt(concept: str | None = None, session_id: str = "", message: str = None) -> str:
    """
    Agent G: Sinh prompt chi tiết cho DALL·E.
    Nếu có concept thì dùng kết hợp concept + design_data + notes.
    Nếu không có concept thì chỉ dùng design_data + notes.
    """

    design_data = {}
    notes = []

    if session_id:
        session = get_session(session_id)
        if session:
            design_data = session.get("design_data", {})
            notes = design_data.get("notes", [])

    context_from_kb = ""
    if message:
        context_from_kb = get_context_from_session(session_id, message)
        print(f"context_from_kb là {context_from_kb}")
    json_part = dumps({k: v for k, v in design_data.items() if k != "notes"}, ensure_ascii=False, indent=2)
    notes_text = "".join(notes) if notes else "(Không có ghi chú bổ sung)"

    # ✅ Prompt template sẽ khác nhau tùy theo việc có concept hay không
    if concept:
        prompt = f"""
C – Context | Bối cảnh
Bạn là một hệ thống con trong chuỗi xử lý của chatbot AI hỗ trợ thiết kế thương hiệu. Người dùng đã lựa chọn một concept cụ thể. Nhiệm vụ hiện tại của bạn là tạo một prompt bằng tiếng Anh để gửi đến DALL·E, nhằm tạo hình ảnh mô phỏng thực tế phù hợp với concept này.

Dữ liệu đầu vào bao gồm:
- `concept`: mô tả ý tưởng thiết kế đã chọn
- `design_data`: dữ liệu kỹ thuật như màu sắc, chất liệu, hình dạng, bố cục (dạng JSON)
- `context_from_kb`: dữ liệu tham khảo từ công ty mẹ của bạn
- `notes_text`: các ghi chú bổ sung từ người dùng (nếu có)

R – Role | Vai trò
Bạn là chuyên gia trong việc tạo prompt sinh ảnh thực tế (photorealistic image generation) cho DALL·E. Bạn sử dụng ngôn ngữ mô tả cụ thể, chính xác, và chi tiết như một đạo diễn sản phẩm hoặc kỹ sư mô phỏng 3D. Bạn không sáng tạo thêm ngoài thông tin được cung cấp.

A – Action | Hành động
- Phân tích kỹ concept và các dữ liệu đi kèm, tham khảo kĩ từ context
- Chuyển toàn bộ thông tin thành mô tả hình ảnh tiếng Anh chi tiết, với phong cách giống như đang mô phỏng sản phẩm thật.
- Mô tả phải bao gồm các yếu tố: bố cục sản phẩm, chất liệu, phối cảnh, nền (background), ánh sáng, góc nhìn, và không khí tổng thể.
- Ưu tiên mô tả ánh sáng thật (realistic lighting), độ nét cao (ultra-sharp), màu sắc chính xác, kết cấu vật liệu cụ thể (textures), background rõ nét.
- Không thêm suy luận hoặc đặc điểm không được cung cấp.

F – Format | Định dạng
- In ra duy nhất một dòng prompt tiếng Anh.
- Không dùng markdown, không xuống dòng, không giải thích, không viết hoa ngẫu nhiên.

T – Target Audience | Đối tượng sử dụng
Đầu ra sẽ được đưa vào API DALL·E để sinh ảnh minh họa sản phẩm thực tế phục vụ thiết kế thương hiệu, trình diễn ý tưởng cho khách hàng hoặc thuyết phục nhà đầu tư.

Input:

Concept:
{concept}

Thông tin kỹ thuật (JSON):
{json_part}

Dữ liệu tham khảo:
{context_from_kb}

Ghi chú bổ sung:
{notes_text}

Chỉ dẫn nghiêm ngặt cho LLM:
- Viết prompt tiếng Anh duy nhất, mô tả hình ảnh thực tế.
- Không thêm tiêu đề, không mô tả thêm, không sinh ảnh.
- Giữ văn phong chính xác, logic, không tưởng tượng.

"""
    else:
        prompt = f"""
C – Context | Bối cảnh
Bạn là một hệ thống con trong chuỗi xử lý của chatbot AI hỗ trợ thiết kế thương hiệu. Người dùng chưa lựa chọn một concept cụ thể. Nhiệm vụ hiện tại của bạn là tạo một prompt bằng tiếng Anh để gửi đến DALL·E, nhằm tạo hình ảnh mô phỏng thực tế phù hợp với thông tin đầu vào.

Dữ liệu đầu vào bao gồm:
- `design_data`: dữ liệu kỹ thuật như màu sắc, chất liệu, hình dạng, bố cục (dạng JSON)
- `context_from_kb`: dữ liệu tham khảo từ công ty mẹ của bạn
- `notes_text`: các ghi chú bổ sung từ người dùng (nếu có)

R – Role | Vai trò
Bạn là chuyên gia trong việc tạo prompt sinh ảnh thực tế (photorealistic image generation) cho DALL·E. Bạn sử dụng ngôn ngữ mô tả cụ thể, chính xác, và chi tiết như một đạo diễn sản phẩm hoặc kỹ sư mô phỏng 3D. Bạn không sáng tạo thêm ngoài thông tin được cung cấp.

A – Action | Hành động
- Phân tích kỹ các dữ liệu đi kèm, tham khảo kĩ từ context
- Chuyển toàn bộ thông tin thành mô tả hình ảnh tiếng Anh chi tiết, với phong cách giống như đang mô phỏng sản phẩm thật.
- Mô tả phải bao gồm các yếu tố: bố cục sản phẩm, chất liệu, phối cảnh, nền (background), ánh sáng, góc nhìn, và không khí tổng thể.
- Ưu tiên mô tả ánh sáng thật (realistic lighting), độ nét cao (ultra-sharp), màu sắc chính xác, kết cấu vật liệu cụ thể (textures), background rõ nét.
- Không thêm suy luận hoặc đặc điểm không được cung cấp.

F – Format | Định dạng
- In ra duy nhất một dòng prompt tiếng Anh.
- Không dùng markdown, không xuống dòng, không giải thích, không viết hoa ngẫu nhiên.

T – Target Audience | Đối tượng sử dụng
Đầu ra sẽ được đưa vào API DALL·E để sinh ảnh minh họa sản phẩm thực tế phục vụ thiết kế thương hiệu, trình diễn ý tưởng cho khách hàng hoặc thuyết phục nhà đầu tư.

Input:

Thông tin kỹ thuật (JSON):
{json_part}

Dữ liệu tham khảo:
{context_from_kb}

Ghi chú bổ sung:
{notes_text}

Chỉ dẫn nghiêm ngặt cho LLM:
- Viết prompt tiếng Anh duy nhất, mô tả hình ảnh thực tế.
- Không thêm tiêu đề, không mô tả thêm, không sinh ảnh.
- Giữ văn phong chính xác, logic, không tưởng tượng.
"""

    result = ask_gpt([{"role": "user", "content": prompt}], temperature=0.7)
    return result.strip()


def extract_concept_index(phrase: str) -> int | None:
    """
    Agent G: Trích số thứ tự concept mà người dùng chọn từ tin nhắn.
    Ví dụ: "Tôi chọn concept 3" → return 2 (zero-based)
    """
    prompt = f"""
Bạn là một hệ thống trích xuất thông tin.
Người dùng sẽ nói về việc chọn một concept thiết kế bằng ngôn ngữ tự nhiên.
Hãy đọc câu nói và trích ra **chỉ số thứ tự** của concept mà họ nhắc đến (số nguyên bắt đầu từ 1).
Nếu không rõ ràng hoặc không có số, trả về null.
Chỉ trả lời bằng số duy nhất (hoặc null). Không giải thích.

Câu: "{phrase}"
"""

    result = ask_gpt([{"role": "user", "content": prompt}], temperature=0.2)
    try:
        num = int(result.strip())
        return num - 1 if num > 0 else None
    except:
        return None
