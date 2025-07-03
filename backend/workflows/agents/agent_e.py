from services.db_service import get_session, store_image_url
from services.openai_service import generate_image

def generate_image_from_selected_concept(session_id: str, resolution: str = "1024x1024") -> dict:
    """
    Agent E: Dựa trên concept đã chọn, sinh ảnh minh hoạ bằng DALL·E.
    Lưu URL ảnh vào DB. Trả về dict {"image_url": "..."} nếu thành công.
    """

    session = get_session(session_id)
    if not session:
        print(f"[Agent E] ❌ Không tìm thấy session: {session_id}")
        return {}

    concept = session.get("selected_concept")
    if not concept:
        print(f"[Agent E] ⚠️ Chưa có concept được chọn.")
        return {}

    # Tạo prompt từ concept
    prompt = f"""Create a detailed visual representation of the following design concept:

{concept}

Generate it in a modern, clean, printable style."""

    try:
        url = generate_image(prompt=prompt, size=resolution)
        if url:
            store_image_url(session_id, url)
            return {"image_url": url}
        else:
            print(f"[Agent E] ❌ Không tạo được ảnh từ DALL·E.")
            return {}
    except Exception as e:
        print(f"[Agent E] ❌ Lỗi khi gọi DALL·E: {e}")
        return {}
