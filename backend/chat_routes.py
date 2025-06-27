from fastapi import APIRouter, Request
from workflows.langgraph_app import build_graph

router = APIRouter()
chatbot = build_graph()

@router.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()

    if body.get("generate_image"):
        concept = body.get("concept", "")
        result = chatbot.invoke({
            "selected_concept": concept,
        })
        return {
            "image_url": result.get("image_url"),
            "reply": "Đây là hình ảnh demo về ý tưởng mà quý khách đã chọn, cảm ơn quý khách đã sử dụng dịch vụ của chúng tôi."
        }

    message = body.get("message", "")
    history = body.get("history", [])
    design_data = body.get("design_data", {})

    result = chatbot.invoke({
        "message": message,
        "history": history,
        "design_data": design_data
    })

    return {
        "reply": result.get("reply", ""),
        "image_url": result.get("image_url"),
        "concepts": result.get("concepts", None)
    }
