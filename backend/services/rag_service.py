# rag_service.py
from services.db_service import get_session, db
from services.openai_service import client as openai_client

VECTOR_COLLECTION = db["knowledge_base"]
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

def get_query_embedding(text: str) -> list[float]:
    try:
        resp = openai_client.embeddings.create(model=EMBEDDING_MODEL, input=text)
        return resp.data[0].embedding
    except Exception as e:
        print(f"[Embedding Error] {e}")
        return []

def query_knowledge_base(query_vec: list[float], k: int = 2) -> list[str]:
    if not query_vec:
        return []
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vec,
                "numCandidates": max(k * 20, 50),
                "limit": k,
                "similarity": "cosine"
            }
        },
        {
            "$project": {
                "content": 1,
                "source": 1,
                "score": {"$meta": "vectorSearchScore"},
                "_id": 0
            }
        }
    ]
    return [doc["content"] for doc in VECTOR_COLLECTION.aggregate(pipeline)]

def build_query_text_from_session(session_id: str, latest_user_message: str) -> str:
    session = get_session(session_id)
    design = session.get("design_data", {}) if session else {}
    
    product_value = design.get("product")
    info = []
    if isinstance(product_value, list) and product_value:
        info.append(f"product: {', '.join(product_value)}")
    elif isinstance(product_value, str) and product_value.strip():
        info.append(f"product: {product_value.strip()}")

    design_ctx = "\n".join(info)
    outer = "Thông tin đã biết:\n" + design_ctx + "\n\n" if design_ctx else ""
    if latest_user_message:
        outer += f"Yêu cầu người dùng: {latest_user_message.strip()}"
    return outer or latest_user_message.strip()


def get_context_from_session(session_id: str, latest_user_message: str, k: int = 2) -> str:
    query_text = build_query_text_from_session(session_id, latest_user_message)
    if not query_text:
        return ""
    embedding = get_query_embedding(query_text)
    docs = query_knowledge_base(embedding, k)
    print(f"[rag_service] Query text:\n{query_text}\n=> Retrieved docs count: {len(docs)}")
    if not docs:
        return "[Không tìm thấy thông tin phù hợp trong kho tri thức]"
    return "\n---\n".join(docs)
