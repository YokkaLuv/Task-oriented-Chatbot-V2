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

def init_session(session_id: str):
    """
    Tạo session mới nếu chưa tồn tại, sử dụng schema chuẩn
    """
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
    """
    Lấy toàn bộ thông tin session
    """
    return collection.find_one({"_id": session_id})


def update_design_data(session_id: str, new_data: dict):
    """
    Gộp thêm dữ liệu vào design_data theo schema chuẩn
    """
    for key, value in new_data.items():
        if key in DEFAULT_DESIGN_DATA:
            collection.update_one(
                {"_id": session_id},
                {"$set": {f"design_data.{key}": value}}
            )
        else:
            print(f"[DB Service] ⚠️ Field không hợp lệ: {key}")

def append_history(session_id: str, message: str):
    """
    Ghi lại lịch sử hội thoại
    """
    collection.update_one(
        {"_id": session_id},
        {"$push": {"history": message}}
    )

def store_concepts(session_id: str, concepts: list[str]):
    """
    Lưu danh sách concept sinh ra từ GPT
    """
    collection.update_one(
        {"_id": session_id},
        {"$set": {"concepts": concepts}}
    )

def store_selected_concept(session_id: str, concept: str):
    """
    Lưu concept mà người dùng đã chọn
    """
    collection.update_one(
        {"_id": session_id},
        {"$set": {"selected_concept": concept}}
    )

def store_image_url(session_id: str, url: str):
    """
    Lưu URL ảnh đã tạo
    """
    collection.update_one(
        {"_id": session_id},
        {"$set": {"image_url": url}}
    )

def get_design_data_for_session(session_id: str) -> dict:
    """
    Trả về phần design_data (riêng) để frontend cập nhật nếu cần
    """
    session = get_session(session_id)
    return session.get("design_data", {}) if session else {}
