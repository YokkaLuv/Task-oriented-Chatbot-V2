from workflows.agents.agent_a import process_message_pipeline
from workflows.agents.agent_f import get_formatted_response

def handle_user_message(message: str, session_id: str) -> str:
    """
    Agent Router: entry point của toàn hệ thống
    - Gửi message đến Agent A xử lý logic
    - Sau đó lấy kết quả phản hồi từ Agent F
    - Trả lại frontend một câu trả lời hoàn chỉnh
    """
    try:
        # B1: Agent A xử lý message → intent → queue → gọi agent B/C/D/E
        process_message_pipeline(message, session_id)

        # B2: Agent F tổng hợp toàn bộ kết quả xử lý từ các agent con
        final_reply = get_formatted_response(session_id)

        return final_reply

    except Exception as e:
        print("[AgentRouter Error]", e)
        return "Hệ thống gặp lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."
