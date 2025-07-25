import os
import glob
from tqdm import tqdm
from langchain.text_splitter import RecursiveCharacterTextSplitter
from services.db_service import db
from services.openai_service import client as openai_client

# --- Cấu hình ---
VECTOR_COLLECTION = db["knowledge_base"]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", ".", " ", ""]
)

# --- Hàm tạo embedding ---
def get_embedding(text: str) -> list[float]:
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"[Embedding Error] {e}")
        return []

# --- Xử lý từng file ---
def process_file(filepath: str):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()
    except Exception as e:
        print(f"[File Error] {filepath} → {e}")
        return

    chunks = splitter.split_text(raw_text)

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        embedding = get_embedding(chunk)
        if not embedding:
            continue

        doc = {
            "source": filepath,
            "content": chunk,
            "embedding": embedding
        }
        VECTOR_COLLECTION.insert_one(doc)

# --- Chạy toàn bộ thư mục ---
def embed_all_documents(root_dir="rag_sources"):
    print(f"[Start] Đọc tài liệu từ thư mục: {root_dir}")

    files = glob.glob(os.path.join(root_dir, "**", "*.txt"), recursive=True)
    print(f"→ Tìm thấy {len(files)} file.")

    for file in tqdm(files, desc="Đang xử lý"):
        process_file(file)

    print("[✅] Hoàn tất quá trình embed và lưu vào MongoDB.")

# --- Entry ---
if __name__ == "__main__":
    embed_all_documents()
