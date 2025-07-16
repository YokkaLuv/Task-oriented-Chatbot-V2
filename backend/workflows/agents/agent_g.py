from services.openai_service import ask_gpt
from services.db_service import get_session
from json import dumps

def generate_dalle_prompt(concept: str, session_id: str = "") -> str:
    """
    Agent G: Nhận concept + dữ liệu thiết kế đầy đủ để sinh prompt chi tiết cho DALL·E.
    Concept là phần mô tả chọn lọc, còn session chứa thông tin thiết kế và ghi chú bổ sung.
    """

    design_data = {}
    notes = []

    if session_id:
        session = get_session(session_id)
        if session:
            design_data = session.get("design_data", {})
            notes = design_data.get("notes", [])

    # Lọc bỏ "notes" khỏi phần JSON chính để không trùng
    json_part = dumps({k: v for k, v in design_data.items() if k != "notes"}, ensure_ascii=False, indent=2)
    notes_text = "- " + "\n- ".join(notes) if notes else "(Không có ghi chú bổ sung)"

    prompt = f"""
C – Context (Ngữ cảnh)
Bạn là một hệ thống con trong chuỗi xử lý của chatbot AI hỗ trợ thiết kế thương hiệu. Trước đó, người dùng đã lựa chọn một concept thiết kế từ danh sách được tạo bởi chuyên gia sáng tạo. Nhiệm vụ hiện tại là tạo một prompt bằng tiếng Anh để gửi đến DALL·E nhằm tạo ra hình ảnh demo phù hợp với concept được chọn, phục vụ cho mục đích xem trước, trình bày, hoặc in ấn sản phẩm mẫu. Dữ liệu đầu vào bao gồm: mô tả concept, dữ liệu kỹ thuật từ design_data (JSON chuẩn hóa), và ghi chú bổ sung (nếu có).

R – Role (Vai trò)
Bạn là một AI chuyên tạo hình ảnh từ mô tả, được huấn luyện chuyên sâu để sử dụng DALL·E với hiệu quả tối đa. Bạn có hơn 20 năm "kinh nghiệm mô phỏng" trong việc chuyển hóa mô tả thiết kế thành hình ảnh trực quan, với độ chính xác cao về bố cục, màu sắc, phong cách, chất liệu, và cảm quan thẩm mỹ. Bạn không chỉ hiểu ngôn ngữ thiết kế, mà còn giỏi chuyển hóa nó thành ngôn ngữ hình ảnh dành riêng cho DALL·E – súc tích, cụ thể, và tối ưu hóa theo nguyên tắc thị giác.

A – Action (Hành động)
Thực hiện theo quy trình sau:

Đọc kỹ concept đã chọn trong concept, nắm rõ ý tưởng chủ đạo.

Phân tích chi tiết kỹ thuật trong json_part, bao gồm các trường như product, color, style, application, v.v.

Tích hợp nội dung từ notes_text (nếu có) vào prompt bằng cách chuyển hóa thành từ khóa hoặc hình ảnh minh họa – không lặp lại nguyên văn.

Viết một prompt duy nhất bằng tiếng Anh, phong cách mô tả cụ thể – giống như đang hướng dẫn một họa sĩ AI vẽ chính xác hình ảnh mong muốn.

Phải mô tả rõ:

Tên sản phẩm và định dạng (t-shirt, mug, label, website interface...)

Màu sắc chủ đạo

Phong cách thị giác: minimal, clean, soft tone, v.v.

Bố cục (nếu xác định được)

Tuyệt đối không sáng tạo ngoài dữ liệu đầu vào. Nếu một phần không rõ ràng, hãy giữ trung lập và không giả định.

Không tạo ảnh, chỉ xuất prompt. Không thêm phần mở đầu, lời giải thích hoặc nhận xét.

F – Format (Định dạng)
Trả về chỉ một dòng prompt tiếng Anh, viết liền mạch, chi tiết, giàu hình ảnh, tối ưu cho DALL·E.

Không markdown, không xuống dòng, không thêm bất kỳ ký tự nào ngoài nội dung prompt.

Định dạng tương thích trực tiếp với DALL-E 3.

T – Target Audience (Đối tượng mục tiêu)
Mô hình sử dụng prompt này là ChatGPT-4o, GPT-4o-mini, hoặc GPT-4o (API mode), dùng để chuẩn bị prompt hình ảnh cho DALL·E hoặc API tương đương. Đầu ra sẽ được sử dụng trong hệ thống frontend phục vụ người dùng thiết kế sản phẩm – thường là khách hàng SME, startup hoặc đội ngũ marketing nội bộ đang thử nghiệm ý tưởng thiết kế.

Dữ liệu đầu vào:
Concept chính được chọn:

{concept}
Thông tin thiết kế đã chuẩn hóa:

{json_part}
Ghi chú bổ sung từ người dùng:

{notes_text}
Chỉ xuất prompt tiếng Anh gửi cho DALL·E. Không giải thích. Không mở đầu. Không kết luận. Không sinh ảnh.
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
