from fastapi import APIRouter, Request
from workflows.agent_router import handle_user_message
from services.db_service import get_session

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()

        message: str = body.get("message", "")
        session_id: str = body.get("session_id", "default")
        selected_concept: str = body.get("selected_concept")

        # Nếu user chọn concept → lưu vào session
        if selected_concept:
            session = get_session(session_id)
            if session is not None:
                session["selected_concept"] = selected_concept

        # Gọi Agent Router xử lý logic toàn bộ pipeline
        result = handle_user_message(message, session_id)

        # ✅ Kiểm tra kỹ kết quả
        if not isinstance(result, dict):
            print("[Chat Router] ⚠️ Agent router không trả về dict.")
            return {
                "reply": "Xin lỗi, tôi chưa xử lý được yêu cầu này.",
                "concepts": None,
                "image_url": None
            }

        # ✅ Trả lại kết quả: reply, concepts, image_url,...
        return result

    except Exception as e:
        print("[Chat Endpoint Error]", e)
        return {
            "reply": "Xin lỗi, đã xảy ra lỗi xử lý yêu cầu của bạn.",
            "concepts": None,
            "image_url": None,
            "error": str(e)
        }
