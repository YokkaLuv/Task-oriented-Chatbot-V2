from services.db_service import get_session, append_evaluation_feedback
from services.openai_service import ask_gpt

def evaluate_reply(session_id: str):
    """
    Đọc 1-2 message cuối trong chatlog, đánh giá chất lượng phản hồi của bot.
    """
    session = get_session(session_id)
    if not session:
        print("[Eval] ❌ Không tìm thấy session.")
        return

    chatlog = session.get("chatlogs", [])
    if len(chatlog) < 2:
        print("[Eval] ⚠️ Chưa đủ dữ liệu để đánh giá.")
        return

    # Lấy 1 user + 1 assistant cuối cùng
    last_pairs = [msg for msg in chatlog if msg["role"] in ("user", "assistant")][-2:]

    if len(last_pairs) < 2:
        return

    prompt = f"""
Bạn là một chuyên gia đánh giá phản hồi AI.

Dưới đây là đoạn hội thoại gần nhất giữa người dùng và chatbot:
User: "{last_pairs[0]['content']}"
Assistant: "{last_pairs[1]['content']}"

Hãy đánh giá phản hồi của chatbot. Nêu rõ:
- Phản hồi có đầy đủ thông tin không?
- Có thiếu ghi chú hoặc dữ liệu nào không?
- Giọng văn và trình bày có phù hợp không?
- Gợi ý cải thiện (nếu có)

Trả kết quả dưới dạng JSON:
{{
  "score": số từ 1-10,
  "issues": [danh sách các điểm yếu nếu có],
  "suggestion": "Câu gợi ý cải thiện prompt hoặc hướng dẫn sinh phản hồi tốt hơn."
}}
"""

    result = ask_gpt([{"role": "user", "content": prompt}], temperature=0.3)

    # Lưu kết quả đánh giá
    append_evaluation_feedback(session_id, result.strip())
    print("[Eval] ✅ Đã đánh giá và lưu feedback.")
