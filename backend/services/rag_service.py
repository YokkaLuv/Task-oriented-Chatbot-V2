from services.db_service import db, get_design_data_for_session
from services.openai_service import client as openai_client

# --- Cấu hình ---
VECTOR_COLLECTION = db["knowledge_base"]
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

# --- Tạo embedding cho truy vấn ---
def get_query_embedding(text: str) -> list[float]:
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[Embedding Error] {e}")
        return []


# --- Tạo đoạn mô tả từ dữ liệu thiết kế trong session ---
def build_design_context(session_id: str) -> str:
    """
    Chuyển dữ liệu thiết kế từ session thành chuỗi mô tả để dùng làm context truy vấn.
    """
    data = get_design_data_for_session(session_id)
    if not data:
        return ""

    context_lines = []
    for key, value in data.items():
        if isinstance(value, list) and value:
            context_lines.append(f"{key}: {', '.join(value)}")
        elif isinstance(value, str) and value.strip():
            context_lines.append(f"{key}: {value.strip()}")

    return "Thông tin thiết kế hiện tại:\n" + "\n".join(context_lines)

# --- Truy vấn vector search từ MongoDB ---
def query_knowledge_base(query: str, k: int = 5) -> list[str]:
    embedding = get_query_embedding(query)
    if not embedding:
        return []

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": embedding,
                "numCandidates": 50,
                "limit": k,
                "similarity": "cosine"
            }
        },
        {
            "$project": {
                "_id": 0,
                "content": 1,
                "source": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    results = VECTOR_COLLECTION.aggregate(pipeline)
    return [doc["content"] for doc in results]


# --- Hàm chính: Lấy context cho RAG dựa vào session + truy vấn ---
def get_context_from_knowledge(query: str, session_id: str, k: int = 5) -> str:
    """
    Trả về nội dung tri thức liên quan dựa vào:
    - thông tin thiết kế trong session
    - truy vấn từ người dùng
    """
    design_context = build_design_context(session_id)
    full_query = f"{design_context}\n\nYêu cầu người dùng: {query}".strip()

    docs = query_knowledge_base(full_query, k)
    if not docs:
        return "[Không tìm thấy thông tin phù hợp trong kho tri thức]"

    return "\n---\n".join(docs)
