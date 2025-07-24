from services.db_service import append_evaluation_feedback, get_chatlog
from services.openai_service import ask_gpt

def evaluate_reply(session_id: str):
    """
    Đọc 1-2 message cuối trong chatlog, đánh giá chất lượng phản hồi của bot.
    """
    chatlog = get_chatlog(session_id)
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

Hãy đánh giá chất lượng phản hồi của chatbot dựa trên cách diễn đạt. Nếu có vấn đề, hãy chỉ rõ. Nếu tốt, hãy nêu lý do. Đưa ra nhận xét và gợi ý cải thiện nếu cần.

Trả kết quả dưới dạng JSON:
{{
  "feedback": "Một đoạn đánh giá ngắn gọn, rõ ràng, bao gồm cả điểm mạnh – điểm yếu – gợi ý cải thiện (nếu có), viết thành văn liền mạch."
}}
""".strip()

    result = ask_gpt([{"role": "user", "content": prompt}], temperature=0.3)

    # Lưu kết quả đánh giá
    append_evaluation_feedback(session_id, result.strip())
    print("[Eval] ✅ Đã đánh giá và lưu feedback.")
