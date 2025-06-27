from fastapi import APIRouter, Request
from workflows.langgraph_app import build_graph

router = APIRouter()
chatbot = build_graph()

@router.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()

    message = body.get("message", "")
    history = body.get("history", [])
    design_data = body.get("design_data", {})
    selected_concept = body.get("selected_concept", None)

    input_state = {
        "message": message,
        "history": history,
        "design_data": design_data
    }

    if selected_concept:
        input_state["selected_concept"] = selected_concept

    result = chatbot.invoke(input_state)

    return {
        "reply": result.get("reply", ""),
        "concepts": result.get("concepts"),
        "image_url": result.get("image_url")
    }
