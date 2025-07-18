from services.db_service import get_session, store_image_url
from services.openai_service import generate_image
from workflows.agents import agent_g
from schemas.design_schema import DEFAULT_DESIGN_DATA

def generate_image_from_selected_concept(session_id: str, resolution: str = "1024x1024") -> dict:
    """
    Agent E: Sinh ảnh minh hoạ từ concept đã chọn hoặc chỉ từ dữ liệu thiết kế.
    Kiểm tra xem thiết kế có đủ thông tin chưa trước khi tạo prompt.
    """

    session = get_session(session_id)
    if not session:
        print(f"[Agent E] ❌ Không tìm thấy session: {session_id}")
        return {"error": "Không tìm thấy phiên thiết kế."}

    design_data = session.get("design_data", {})
    concept = session.get("selected_concept", None)

    # ✅ Kiểm tra thiếu thông tin (trừ notes)
    missing_fields = [
        field for field in DEFAULT_DESIGN_DATA
        if field != "notes" and not design_data.get(field)
    ]

    if missing_fields:
        print(f"[Agent E] ⚠️ Thiếu thông tin thiết kế: {missing_fields}")
        return {
            "error": f"Không thể tạo ảnh vì thiếu thông tin: {', '.join(missing_fields)}"
        }

    # ✅ Dù có concept hay không, vẫn tạo prompt từ dữ liệu + concept nếu có
    try:
        dalle_prompt = agent_g.generate_dalle_prompt(concept=concept or "", session_id=session_id)
        print(f"[Agent E] 🎯 Prompt gửi tới DALL·E:\n{dalle_prompt}\n")

        url = generate_image(prompt=dalle_prompt, size=resolution)
        if url:
            store_image_url(session_id, url)
            print(f"[Agent E] ✅ Đã tạo ảnh thành công: {url}")
            return {"image_url": url}
        else:
            print(f"[Agent E] ❌ Không tạo được ảnh từ DALL·E.")
            return {"error": "Không thể tạo ảnh từ DALL·E."}

    except Exception as e:
        print(f"[Agent E] ❌ Lỗi khi gọi DALL·E: {e}")
        return {"error": f"Lỗi khi gọi DALL·E: {str(e)}"}
