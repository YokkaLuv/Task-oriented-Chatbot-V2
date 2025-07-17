from services.db_service import get_session, store_image_url
from services.openai_service import generate_image
from workflows.agents import agent_g

def generate_image_from_selected_concept(session_id: str, resolution: str = "1024x1024") -> dict:
    """
    Agent E: Dựa trên concept đã chọn (nếu có), hoặc dữ liệu thiết kế, sinh ảnh minh hoạ bằng DALL·E.
    Gọi Agent G để tạo prompt chi tiết.
    Lưu URL ảnh vào DB. Trả về dict {"image_url": "..."} nếu thành công.
    """

    session = get_session(session_id)
    if not session:
        print(f"[Agent E] ❌ Không tìm thấy session: {session_id}")
        return {"error": "Không tìm thấy phiên thiết kế."}

    design_data = session.get("design_data", {})
    if not design_data:
        print(f"[Agent E] ❌ Thiếu dữ liệu thiết kế để tạo ảnh.")
        return {"error": "Chưa có đủ dữ liệu thiết kế để tạo ảnh."}

    concept = session.get("selected_concept")

    try:
        # ✅ Nếu có concept → ưu tiên dùng
        if concept:
            print("[Agent E] 🧠 Đang dùng concept để sinh prompt.")
        else:
            print("[Agent E] 🔄 Không có concept, sẽ dùng dữ liệu thiết kế để sinh prompt.")

        dalle_prompt = agent_g.generate_dalle_prompt(concept=concept, session_id=session_id)
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
