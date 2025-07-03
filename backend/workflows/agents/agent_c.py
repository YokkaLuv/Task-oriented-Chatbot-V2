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
    missing = []

    for field in DEFAULT_DESIGN_DATA:
        if not design_data.get(field):  # None, "", [] đều coi như thiếu
            missing.append(field)

    return {"missing_fields": missing} if missing else {}
