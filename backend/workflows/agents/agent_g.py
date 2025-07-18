from services.openai_service import ask_gpt
from services.db_service import get_session
from json import dumps

def generate_dalle_prompt(concept: str | None = None, session_id: str = "") -> str:
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

    json_part = dumps({k: v for k, v in design_data.items() if k != "notes"}, ensure_ascii=False, indent=2)
    notes_text = "- " + "\n- ".join(notes) if notes else "(Không có ghi chú bổ sung)"

    # ✅ Prompt template sẽ khác nhau tùy theo việc có concept hay không
    if concept:
        prompt = f"""
C – Context | Bối cảnh
Bạn là một hệ thống con trong chuỗi xử lý của chatbot AI hỗ trợ thiết kế thương hiệu. Người dùng đã lựa chọn một concept cụ thể. Nhiệm vụ hiện tại của bạn là tạo một prompt bằng tiếng Anh để gửi đến DALL·E, nhằm tạo hình minh hoạ phù hợp với concept này.
Dữ liệu đầu vào bao gồm:

concept: mô tả ý tưởng thiết kế đã chọn

design_data: dữ liệu kỹ thuật (màu sắc, chất liệu, kiểu dáng, bố cục, v.v.) ở định dạng JSON

notes_text: các ghi chú bổ sung từ người dùng (có thể có hoặc không)

R – Role | Vai trò
Bạn là một chuyên gia hàng đầu trong việc chuyển đổi văn bản mô tả thiết kế thành prompt hình ảnh cho mô hình DALL·E. Bạn có kiến thức sâu rộng về:

Ngôn ngữ mô tả hình ảnh

Từ vựng chuyên ngành thiết kế, phối cảnh, bố cục, chất liệu, ánh sáng

Tối ưu hóa đầu vào để mô hình sinh ảnh tạo ra hình ảnh trực quan, chính xác và đẹp mắt
Bạn không bịa đặt thông tin. Bạn chỉ diễn đạt lại thông tin đã cung cấp bằng ngôn ngữ mô tả giàu hình ảnh.

A – Action | Hành động
Phân tích kỹ concept để hiểu chủ đề, phong cách, hoặc thông điệp thị giác.

Trích xuất thông tin từ design_data (JSON) để lấy các thuộc tính

Nếu có notes_text, bạn lồng ghép các yếu tố hợp lý từ phần ghi chú này vào mô tả.

Viết lại toàn bộ thành một prompt tiếng Anh duy nhất, giàu tính hình ảnh và định hướng rõ ràng cho DALL·E.

Giữ giọng văn mô tả trung tính, khách quan; không thêm thắt trí tưởng tượng hay sáng tạo ngoài phạm vi dữ liệu gốc.

Không giải thích lại, không chào hỏi, không định dạng markdown. Chỉ in ra prompt.

F – Format | Định dạng
Output: Dòng prompt chi tiết bằng tiếng Anh, không markdown, không xuống dòng, không tiêu đề, không giải thích.

Cấu trúc câu nên thiên về mô tả thị giác, bố cục, màu sắc, ánh sáng và chất liệu.

Tránh lặp từ, tránh liệt kê khô khan – hãy viết như đang mô tả cho một nghệ sĩ AI có thể "vẽ lại" chính xác cảnh tượng.

T – Target Audience | Đối tượng sử dụng
Prompt được sử dụng bởi hệ thống sinh ảnh minh hoạ tự động cho các thiết kế thương hiệu, sản phẩm hoặc chiến dịch marketing.

Đối tượng hưởng lợi: nhà sáng lập startup, marketer nội bộ, đội ngũ sáng tạo đang cần bản vẽ/ảnh mô phỏng nhanh để trình bày ý tưởng hoặc thuyết phục đối tác đầu tư.

Đầu ra này sẽ được đưa trực tiếp vào API DALL·E để sinh ảnh phục vụ các bước tiếp theo trong hệ thống.

📥 Input Template (Biến đầu vào):

Concept:
{concept}

Thông tin thiết kế (JSON):
{json_part}

Ghi chú bổ sung (nếu có):
{notes_text}
🔒 Chỉ dẫn nghiêm ngặt cho LLM
Chỉ in ra prompt tiếng Anh gửi cho DALL·E

Không giải thích

Không sinh ảnh

Không mở đầu, không kết luận, không gợi ý thêm
"""
    else:
        prompt = f"""
C – Context | Bối cảnh
Bạn là một hệ thống con trong chuỗi xử lý AI của chatbot thiết kế thương hiệu. Trong trường hợp người dùng chưa chọn concept cụ thể, hệ thống cần sinh một prompt tiếng Anh gửi đến DALL·E để tạo ra ảnh minh hoạ sản phẩm theo dữ liệu thiết kế đã có.
Dữ liệu đầu vào bao gồm:

design_data: thông tin kỹ thuật chuẩn hoá (màu sắc, chất liệu, phong cách, bố cục, loại sản phẩm, v.v.), định dạng JSON.

notes_text: các ghi chú bổ sung từ người dùng, giúp làm rõ hoặc nhấn mạnh một số đặc điểm thị giác quan trọng (nếu có).

R – Role | Vai trò
Bạn là một chuyên gia hàng đầu về tạo prompt mô tả hình ảnh cho các hệ thống AI như DALL·E. Bạn có:

Hiểu biết sâu sắc về từ vựng thiết kế (design language)

Khả năng dịch dữ liệu kỹ thuật thành mô tả thị giác bằng tiếng Anh

Kỹ năng mô tả chi tiết bố cục, chất liệu, ánh sáng, màu sắc mà không thêm thắt hay sáng tạo ngoài thông tin gốc

A – Action | Hành động
Đọc và phân tích kỹ design_data dạng JSON – trích xuất các trường quan trọng như product_type, color, material, style, layout, size, v.v.

Nếu có notes_text, kết hợp các mô tả bổ sung từ người dùng vào phần diễn đạt phù hợp.

Viết một dòng prompt tiếng Anh duy nhất, sử dụng ngôn ngữ thị giác phong phú, miêu tả chi tiết:

Loại sản phẩm

Màu sắc chủ đạo

Chất liệu cấu thành

Phong cách tổng thể (style)

Các chi tiết đặc biệt nếu có (dựa trên notes_text)

Không bịa đặt thêm nội dung không tồn tại. Chỉ sử dụng thông tin đã được cung cấp.

F – Format | Định dạng
Chỉ trả về một dòng prompt tiếng Anh – không xuống dòng, không giải thích, không đánh dấu markdown.

Câu văn cần rõ ràng, hình ảnh hóa tốt, giàu yếu tố mô tả (visual language), theo phong cách hướng dẫn cho nghệ sĩ AI.

Tránh cấu trúc danh sách rời rạc – hãy diễn đạt như một mô tả hoàn chỉnh.

Cố gắng hướng tới hình ảnh càng thực tế càng tốt, như thể là hình ảnh thực tế ngoài đời.

T – Target Audience | Đối tượng sử dụng
Output được sử dụng bởi giao diện người dùng của hệ thống thiết kế thương hiệu tự động, khi người dùng yêu cầu sinh ảnh minh hoạ trước khi chọn concept.

Người sử dụng cuối cùng có thể là: nhà sáng lập startup, nhân viên marketing, hoặc nhóm sáng tạo muốn hình dung sản phẩm ở giai đoạn phác thảo.

Prompt sẽ được sử dụng để gọi API sinh ảnh minh họa thông qua DALL·E, nên cần mô tả chính xác, rõ ràng, giàu hình ảnh nhưng không vượt quá thông tin đã có.

📥 Input Template (Biến đầu vào):
Thông tin thiết kế (JSON):
{json_part}

Ghi chú bổ sung (nếu có):
{notes_text}
🔒 Chỉ dẫn nghiêm ngặt cho LLM
Chỉ xuất một dòng prompt tiếng Anh gửi cho DALL·E

Không giải thích

Không sinh ảnh

Không mở đầu, không kết luận, không markdown
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
