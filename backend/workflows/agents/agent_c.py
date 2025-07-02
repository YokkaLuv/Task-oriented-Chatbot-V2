from backend.services.db_service import get_session

# Danh sách các trường bắt buộc trong thiết kế
REQUIRED_FIELDS = [
    "product",
    "color",
    "material",
    "style",
    "audience"
]

def check_missing_fields(session_id: str) -> list[str]:
    """
    Agent C: Kiểm tra các trường còn thiếu trong design_data.
    Trả về danh sách các trường bị thiếu.
    """

    session = get_session(session_id)
    if not session:
        print(f"[Agent C] ⚠️ Không tìm thấy session: {session_id}")
        return REQUIRED_FIELDS.copy()  # nếu chưa có gì thì xem như thiếu hết

    design_data = session.get("design_data", {})
    missing = []

    for field in REQUIRED_FIELDS:
        if field not in design_data or not design_data[field]:
            missing.append(field)

    return missing
