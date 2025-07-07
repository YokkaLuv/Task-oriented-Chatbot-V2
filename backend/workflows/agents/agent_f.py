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
Bạn là một trợ lý AI chuyên nghiệp trong lĩnh vực thiết kế sản phẩm. Nhiệm vụ của bạn là:
- Tổng hợp kết quả phân tích từ các module xử lý riêng biệt (dưới đây)
- Tạo ra một phản hồi duy nhất, mượt mà, tự nhiên như một người hỗ trợ thực thụ

Dữ liệu đầu vào có thể bao gồm:
- missing_fields: danh sách thông tin người dùng chưa cung cấp
- concepts: danh sách các ý tưởng thiết kế
- image_url: đường dẫn ảnh demo (nếu đã có)

Yêu cầu:
- Nếu có missing_fields: hãy nói rõ còn thiếu gì và khuyến khích người dùng bổ sung.
- Nếu có concepts: hãy giới thiệu ngắn gọn rằng đã sinh xong concept và đề nghị người dùng xem qua.
- Nếu có image_url: hãy giới thiệu rằng ảnh đã được tạo thành công và đưa link ảnh ra.
- Nếu không có gì cụ thể, hãy xác nhận rằng thông tin đã được ghi nhận.

Kết quả:
- Trả lại chỉ một đoạn văn duy nhất, không phân tích dữ liệu, không giải thích thêm, văn phong thân thiện và chuyên nghiệp.

--- Dữ liệu đầu vào ---
{input_json}
--- Hết dữ liệu ---
Trả lời:
"""

    reply = ask_gpt([{"role": "user", "content": prompt}], temperature=0.5).strip()

    # Gắn concept (nếu có) vào cuối reply luôn
    if merged["concepts"]:
        concept_text = "\n\n" + "\n\n".join(merged["concepts"])
        reply += f"\n\n---\n**Các ý tưởng thiết kế:**\n{concept_text}"

    return {
        "reply": reply,
        "image_url": merged["image_url"]
    }
