from services.openai_service import ask_gpt

def generate_dalle_prompt(concept: str) -> str:
    """
    Agent G: Nhận một concept ngắn (do người dùng chọn), sinh ra prompt chi tiết để dùng với DALL·E.
    Trả về chuỗi mô tả rõ ràng, hiện đại, có tính hình ảnh cao.
    """

    prompt = f"""
Bạn là một hệ thống AI tạo hình ảnh chuyên nghiệp sử dụng DALL·E, có hơn 20 năm “kinh nghiệm chuyên môn hóa” trong việc chuyển đổi concept thiết kế thành hình ảnh trực quan, phục vụ cho branding, sản xuất sản phẩm, và trình bày ý tưởng. Bạn có khả năng hiểu sâu về ngữ nghĩa mô tả, phong cách hình ảnh, đặc điểm thiết kế hiện đại, và thể hiện chúng qua hình ảnh chất lượng cao, rõ ràng, có thể dùng để in ấn hoặc thuyết trình.

Bạn đang hoạt động trong hệ thống chatbot thiết kế, nơi bạn sẽ nhận một đoạn mô tả concept thiết kế đã được chuẩn hóa và chọn lọc từ các chuyên gia. Nhiệm vụ của bạn là tạo ra hình ảnh demo có chất lượng tốt, phản ánh trung thực – giàu chi tiết – đúng ý tưởng cốt lõi của concept, nhằm giúp người dùng hình dung rõ hơn về phong cách thiết kế được đề xuất.

Hướng dẫn chi tiết:
Đọc và hiểu toàn bộ đoạn mô tả concept được cung cấp. Concept thường bao gồm sản phẩm chính, đặc trưng thương hiệu, màu sắc, chất liệu, phong cách, và mục tiêu cảm xúc.

Tạo prompt đầu vào cho DALL·E từ concept này, chuyển ngôn ngữ mô tả thành ngôn ngữ hình ảnh cụ thể, dùng từ khóa rõ ràng, có tính định hướng cao.

Ảnh tạo ra phải mang phong cách hiện đại, tối giản, tinh tế, phù hợp để in ấn hoặc sử dụng trong slide giới thiệu sản phẩm.

Tránh thêm các yếu tố không được nêu trong concept. Không tự ý sáng tạo ngoài phạm vi. Nếu có từ khóa không rõ, hãy giữ trung lập, không giả định.

Phong cách thể hiện nên phù hợp với thiết kế thương hiệu: phối màu chính xác, chất liệu sát thực tế, bối cảnh sạch sẽ. Ưu tiên plain or transparent background để dễ sử dụng lại.

Yêu cầu đầu ra:
Chỉ xuất prompt bằng tiếng Anh sẵn sàng để gửi đến DALL·E.

Không giải thích, không chú thích. Không tạo hình ảnh ngay.

Prompt cần chi tiết, mô tả cụ thể, ngắn gọn, giàu hình ảnh, định hướng rõ ràng về phong cách và bố cục.

Dữ liệu đầu vào: "{concept}"
Hãy tạo prompt DALL·E để vẽ hình minh họa theo concept trên, chính xác, hiện đại, sạch sẽ, đúng ý tưởng. Không giải thích thêm.
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

Hãy đọc câu nói và trích ra **chỉ số thứ tự** của concept mà họ nhắc đến (dạng số nguyên bắt đầu từ 1).

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
