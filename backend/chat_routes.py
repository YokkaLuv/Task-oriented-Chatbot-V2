from fastapi import APIRouter, Request
from services.openai_service import build_message_history, ask_gpt, generate_image_from_data, generate_concepts_from_transcript

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()

    if body.get("generate_concepts"):
        transcript = body.get("transcript", "")
        concepts = generate_concepts_from_transcript(transcript)
        return { "concepts": concepts }

    if body.get("generate_image"):
        concept = body.get("concept", "")
        try:
            image_url = generate_image_from_data({ "selected_concept": concept })
            return { "image_url": image_url }
        except Exception as e:
            return { "error": f"Image generation failed: {e}" }

    message = body.get("message", "")
    history = body.get("history", [])
    design_data = body.get("design_data", {})

    messages = build_message_history(history + [{"role": "user", "content": message}])
    reply = ask_gpt(messages)

    return {
        "reply": reply,
        "image_url": None  
    }
