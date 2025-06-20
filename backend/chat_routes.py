from fastapi import APIRouter, Request
from services.openai_service import build_message_history, ask_gpt, generate_image_from_data

router = APIRouter()

# Endpoint chính để xử lý chat
@router.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    message = body.get("message", "")
    history = body.get("history", [])  # Expect [{role: "user"|"assistant", content: "..."}]
    design_data = body.get("design_data", {})  # Optional: structured fields nếu có

    messages = build_message_history(history + [{"role": "user", "content": message}])
    reply = ask_gpt(messages)

    image_url = None
    if design_data and isinstance(design_data, dict):
        try:
            image_url = generate_image_from_data(design_data)
        except Exception as e:
            print(f"Image generation failed: {e}")

    return {"reply": reply, "image_url": image_url}