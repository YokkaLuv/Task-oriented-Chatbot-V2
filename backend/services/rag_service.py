# rag_service.py
from services.db_service import db
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

# --- Truy vấn vector search từ MongoDB ---
def query_knowledge_base(query: str, k: int = 5) -> list[str]:
    embedding = get_query_embedding(query)
    if not embedding:
        return []

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",  # Đúng tên index bạn đã đặt trong MongoDB
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

def get_context_from_knowledge(query: str, k: int = 5) -> str:
    docs = query_knowledge_base(query, k)
    if not docs:
        return "[Không tìm thấy thông tin phù hợp trong kho tri thức]"
    return "\n---\n".join(docs)
