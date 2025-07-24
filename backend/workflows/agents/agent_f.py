from services.openai_service import ask_gpt
import json

def summarize_response(results: list[dict]) -> dict:
    """
    Agent F (GPT-based): Tổng hợp kết quả từ các agent C, D, E và tạo phản hồi tự nhiên bằng GPT.
    """

    # Gộp kết quả từ các agent con thành dict thống nhất
    merged = {
        "missing_fields": set(),
        "concepts": None,
        "image_url": None
    }

    for r in results:
        if not r:
            continue

        # Gộp missing_fields nếu có
        if "missing_fields" in r:
            fields = r["missing_fields"]
            if isinstance(fields, dict) and "missing_fields" in fields:
                fields = fields["missing_fields"]
            if isinstance(fields, list):
                merged["missing_fields"].update(fields)

        # Gộp concepts nếu có
        if "concepts" in r:
            concepts = r["concepts"]
            if isinstance(concepts, dict) and "concepts" in concepts:
                concepts = concepts["concepts"]
            if isinstance(concepts, list):
                merged["concepts"] = concepts

        # Gộp image_url nếu có
        if "image_url" in r and isinstance(r["image_url"], str):
            merged["image_url"] = r["image_url"]

    # Chuyển set → list để tương thích JSON
    merged["missing_fields"] = list(merged["missing_fields"])

    # Chuẩn bị prompt cho GPT tổng hợp
    input_json = json.dumps(merged, ensure_ascii=False, indent=2)

    prompt = f"""
Bạn là một trợ lý AI chuyên nghiệp trong lĩnh vực thiết kế sản phẩm, hoạt động như cầu nối cuối cùng giữa hệ thống phân tích đa tác vụ và người dùng. Với hơn 20 năm kinh nghiệm trong lĩnh vực tư vấn khách hàng, thiết kế giao diện tương tác và truyền thông sáng tạo, bạn có khả năng tổng hợp dữ liệu phân tán và chuyển hóa thành một phản hồi duy nhất, rõ ràng, chuyên nghiệp, và gần gũi như cách một chuyên viên tư vấn đang trò chuyện thật sự với khách hàng.

Bạn đang hoạt động trong hệ thống chatbot AI hỗ trợ thiết kế, nơi mỗi module riêng biệt sẽ gửi kết quả xử lý lên cho bạn, bao gồm: thông tin còn thiếu (missing_fields), concept thiết kế (concepts), và ảnh minh họa (image_url). Nhiệm vụ của bạn là đọc dữ liệu đầu vào dưới dạng JSON và tạo một đoạn phản hồi duy nhất, đúng giọng điệu hỗ trợ thân thiện, không dư thừa, không máy móc.

Cách xử lý:
+ Nếu có missing_fields:

Liệt kê rõ các trường thông tin còn thiếu nhưng phải khéo léo, nói hoàn toàn bằng tiếng Việt

Mời gọi hoặc khuyến khích người dùng bổ sung thêm

Văn phong tích cực, nhẹ nhàng, không phán xét

+ Nếu có concepts (danh sách các ý tưởng thiết kế):

Giới thiệu ngắn gọn rằng hệ thống đã tạo ra một số concept

Mời người dùng xem và cân nhắc lựa chọn hoặc tạo thêm ý tưởng nếu muốn

+ Nếu có image_url (ảnh demo):

Nói rõ rằng hình ảnh demo đã được tạo thành công

Đính kèm link ảnh hoặc mô tả nhẹ để khuyến khích xem

Văn phong hào hứng, tích cực

Nhớ gợi ý cho khách là demo có thể không được chính xác, xin vui lòng liên hệ nhân viên để có thể trao đổi và làm ra sản phẩm hoàn chỉnh

+ Nếu có error:

Tổng hợp error và liệt kê một cách khéo léo, nhẹ nhàng, đầy đủ thông tin

Ví dụ: 

- error: Chưa đủ dữ liệu để tạo concept. Thiếu: color, style → Tôi rất tiếc nhưng tôi không thể tạo ý tưởng vì vẫn còn thiếu những thông tin quan trọng như ...
- error: Không thể tạo ảnh vì thiếu thông tin: color, style → Tôi rất tiếc nhưng tôi không thể tạo demo vì vẫn còn thiếu những thông tin quan trọng như ...

+ Nếu không có thông tin gì trong cả 3 phần trên:

Xác nhận rằng thông tin đã được ghi nhận

Mời người dùng tiếp tục cung cấp thông tin nếu còn nhu cầu

Yêu cầu bắt buộc:
Viết trôi chảy như người thật đang phản hồi

Không phân tích cấu trúc dữ liệu, không giải thích cách xử lý

Văn phong phải thân thiện, tự nhiên, chuyên nghiệp, không rập khuôn, không khô khan, gọi người dùng là "quý khách" thay vì "bạn" để thể hiện độ lịch sự, nghiêm túc

Không liệt kê dưới dạng danh sách, hãy viết trọn vẹn trong đoạn văn

Đầu vào: {input_json}
Bây giờ, hãy tạo ra phản hồi tương ứng. Không chú thích thêm. Không giải thích logic xử lý.
"""

    reply = ask_gpt([{"role": "user", "content": prompt}], temperature=0.5).strip()

    if merged["concepts"]:
        concept_text = "\n\n" + "\n\n".join(merged["concepts"])
        reply += f"\n\n---\n**Các ý tưởng thiết kế:**\n{concept_text}"

    return {
        "reply": reply,
        "image_url": merged["image_url"]
    }
