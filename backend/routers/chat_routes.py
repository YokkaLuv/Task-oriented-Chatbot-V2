from fastapi import APIRouter, Request
from workflows.agents.agent_a import agent_a_router
from workflows.agents.agent_b import get_design_data_for_session  # để trả về dữ liệu cập nhật nếu cần

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    try:
        body = await request.json()

        message: str = body.get("message", "")
        session_id: str = body.get("session_id", "default")

        # Gọi Agent A xử lý message (route intent → agent con)
        reply = agent_a_router(message, session_id)

        # Lấy lại design_data hiện tại nếu frontend cần cập nhật
        design_data = get_design_data_for_session(session_id)

        return {
            "reply": reply,
            "design_data": design_data
        }
    except Exception as e:
        return {
            "error": str(e),
            "reply": "Xin lỗi, đã xảy ra lỗi xử lý yêu cầu của bạn."
        }
