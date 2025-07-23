import os
from pymongo import MongoClient
from dotenv import load_dotenv
from schemas.design_schema import DEFAULT_DESIGN_DATA

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME", "designbot")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "sessions")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
chatlog_collection = db["chatlogs"]

def init_session(session_id: str):
    collection.update_one(
        {"_id": session_id},
        {
            "$setOnInsert": {
                "design_data": DEFAULT_DESIGN_DATA.copy(),
                "concepts": [],
                "selected_concept": None,
                "image_url": None,
                "history": []
            }
        },
        upsert=True
    )

def get_session(session_id: str) -> dict | None:
    return collection.find_one({"_id": session_id})

def update_design_data(session_id: str, new_data: dict):
    session = get_session(session_id)
    if not session:
        print(f"[DB Service] ❌ Không tìm thấy session: {session_id}")
        return

    design_data = session.get("design_data", {})

    for key, value in new_data.items():
        if key not in DEFAULT_DESIGN_DATA:
            print(f"[DB Service] ⚠️ Field không hợp lệ: {key}")
            continue

        default_type = type(DEFAULT_DESIGN_DATA[key])

        # Trường multi-value dạng list (e.g. color, material)
        if default_type is list:
            current_values = design_data.get(key, [])
            if not isinstance(current_values, list):
                current_values = []

            if isinstance(value, str):
                value = [value]
            elif not isinstance(value, list):
                print(f"[DB Service] ⚠️ Giá trị không hợp lệ cho list: {key} → {value}")
                continue

            merged = list(set(current_values + value))
            collection.update_one(
                {"_id": session_id},
                {"$set": {f"design_data.{key}": merged}}
            )

        # Trường đơn trị: ghi đè luôn
        else:
            collection.update_one(
                {"_id": session_id},
                {"$set": {f"design_data.{key}": value}}
            )

def append_notes_to_design_data(session_id: str, note: str):
    """
    Ghi chú thêm vào trường design_data.notes
    """
    note = note.strip()
    if not note:
        return

    session = get_session(session_id)
    current_notes = session.get("design_data", {}).get("notes", "").strip()
    updated_notes = f"{current_notes}\n{note}".strip() if current_notes else note

    collection.update_one(
        {"_id": session_id},
        {"$set": {"design_data.notes": updated_notes}}
    )
    print(f"[DB Service] 📝 Ghi chú thêm vào notes: {note}")

def append_history(session_id: str, message: str):
    collection.update_one(
        {"_id": session_id},
        {"$push": {"history": message}}
    )

def store_concepts(session_id: str, concepts: list[str]):
    collection.update_one(
        {"_id": session_id},
        {"$set": {"concepts": concepts}}
    )

def store_selected_concept(session_id: str, concept: str):
    collection.update_one(
        {"_id": session_id},
        {"$set": {"selected_concept": concept}}
    )

def store_image_url(session_id: str, url: str):
    collection.update_one(
        {"_id": session_id},
        {"$set": {"image_url": url}}
    )

def get_design_data_for_session(session_id: str) -> dict:
    session = get_session(session_id)
    return session.get("design_data", {}) if session else {}

def select_concept_by_index(session_id: str, index: int):
    session = get_session(session_id)
    if not session or "concepts" not in session:
        print(f"[DB] ❌ Không tìm thấy danh sách concept để chọn (session_id: {session_id})")
        return

    concepts = session.get("concepts", [])
    if not concepts:
        print(f"[DB] ⚠️ Danh sách concept rỗng.")
        return

    if 0 <= index < len(concepts):
        selected = concepts[index]
        store_selected_concept(session_id, selected)
        print(f"[DB] ✅ Đã lưu concept được chọn: {selected}")
    else:
        print(f"[DB] ⚠️ Index concept không hợp lệ: {index}")

def remove_design_fields(session_id: str, fields: list[str]):
    """
    Xóa các field chỉ định khỏi design_data trong session.
    Nếu field là list → xóa toàn bộ.
    Nếu field là giá trị đơn → xóa bằng None.
    """
    if not fields:
        return

    unset_ops = {}
    for field in fields:
        if field not in DEFAULT_DESIGN_DATA:
            print(f"[DB Service] ⚠️ Field không hợp lệ để xoá: {field}")
            continue

        if isinstance(DEFAULT_DESIGN_DATA[field], list):
            unset_ops[f"design_data.{field}"] = []
        else:
            unset_ops[f"design_data.{field}"] = None

    if unset_ops:
        collection.update_one(
            {"_id": session_id},
            {"$set": unset_ops}
        )
        print(f"[DB Service] ✅ Đã xoá field: {list(unset_ops.keys())}")

def remove_specific_field_values(session_id: str, field: str, value: str):
    """
    Xoá một giá trị cụ thể trong các field dạng list của design_data.
    Ví dụ: xoá 'đỏ' khỏi color.
    """
    if field not in DEFAULT_DESIGN_DATA:
        print(f"[DB Service] ❌ Field không hợp lệ: {field}")
        return

    if not isinstance(DEFAULT_DESIGN_DATA[field], list):
        print(f"[DB Service] ⚠️ Field '{field}' không phải dạng list, không thể xoá giá trị cụ thể.")
        return

    session = get_session(session_id)
    if not session:
        print(f"[DB Service] ❌ Không tìm thấy session: {session_id}")
        return

    current_values = session.get("design_data", {}).get(field, [])
    if not isinstance(current_values, list):
        print(f"[DB Service] ⚠️ Field '{field}' hiện không phải list.")
        return

    new_values = [v for v in current_values if str(v).strip().lower() != value.strip().lower()]
    collection.update_one(
        {"_id": session_id},
        {"$set": {f"design_data.{field}": new_values}}
    )
    print(f"[DB Service] 🧹 Đã xoá '{value}' khỏi '{field}' → Còn lại: {new_values}")

def append_chatlog(session_id: str, message: dict):
    """
    Ghi một message vào chatlog của session (không có timestamp).
    Message có dạng: {"role": "user" | "assistant", "content": "..."}
    """
    result = chatlog_collection.find_one({"session_id": session_id})
    
    if result:
        chatlog_collection.update_one(
            {"session_id": session_id},
            {"$push": {"chat_history": message}}
        )
    else:
        chatlog_collection.insert_one({
            "session_id": session_id,
            "chat_history": [message]
        })


def get_chatlog(session_id: str) -> list:
    """
    Truy xuất toàn bộ chatlog của session.
    Trả về list các message: [{"role": ..., "content": ...}, ...]
    """
    doc = chatlog_collection.find_one({"session_id": session_id})
    return doc["chat_history"] if doc and "chat_history" in doc else []

def append_evaluation_feedback(session_id: str, feedback: str):
    collection.update_one(
        {"_id": session_id},
        {"$push": {"evaluation_feedback": feedback}}
    )