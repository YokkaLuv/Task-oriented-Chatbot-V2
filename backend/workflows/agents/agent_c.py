from services.db_service import get_session
from schemas.design_schema import DEFAULT_DESIGN_DATA

def check_missing_fields(session_id: str) -> dict:
    """
    Agent C: Kiểm tra các trường còn thiếu trong design_data.
    Trả về dict chứa 'missing_fields' nếu có.
    """

    session = get_session(session_id)
    if not session:
        print(f"[Agent C] ⚠️ Không tìm thấy session: {session_id}")
        return {"missing_fields": list(DEFAULT_DESIGN_DATA.keys())}

    design_data = session.get("design_data", {})
    OPTIONAL_FIELDS = ["notes"]  # Các field không bắt buộc
    REQUIRED_FIELDS = [key for key in DEFAULT_DESIGN_DATA if key not in OPTIONAL_FIELDS]

    missing = []

    for field in REQUIRED_FIELDS:
        value = design_data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()) or (isinstance(value, list) and not value):
            missing.append(field)

    return {"missing_fields": missing} if missing else {}
