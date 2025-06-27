from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from services.openai_service import (
    ask_gpt,
    generate_concepts_from_transcript,
    generate_image_from_data
)

class ChatState(TypedDict, total=False):
    message: str
    history: list[dict]
    design_data: dict
    reply: str
    concepts: list[str]
    selected_concept: str
    image_url: Optional[str]

def collect_message(state: ChatState) -> ChatState:
    message = state["message"]
    history = state.get("history", [])
    
    reply = ask_gpt(history + [{"role": "user", "content": message}])
    
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    
    return {
        **state,
        "reply": reply,
        "history": history
    }

REQUIRED_KEYS = [
    "business", "product", "audience", 
    "colors", "style", "contact_information"
]

def route_after_collect(state: ChatState) -> str:
    data = state.get("design_data", {})
    filled_keys = [key for key in REQUIRED_KEYS if data.get(key)]
    if len(filled_keys) >= len(REQUIRED_KEYS):
        return "suggest_concepts"
    else:
        return "wait_for_more_info"

def suggest_concepts(state: ChatState) -> ChatState:
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in state.get("history", []))
    concepts = generate_concepts_from_transcript(transcript)
    return {**state, "concepts": concepts}

def wait_for_more_info(state: ChatState) -> ChatState:
    return state

def generate_image(state: ChatState) -> ChatState:
    concept = state.get("selected_concept", "")
    image_url = generate_image_from_data({"selected_concept": concept})
    return {**state, "image_url": image_url}

def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node("collect", collect_message)
    graph.add_node("suggest_concepts", suggest_concepts)
    graph.add_node("wait_for_more_info", wait_for_more_info)
    graph.add_node("generate", generate_image)

    graph.set_entry_point("collect")

    graph.add_conditional_edges(
        "collect",
        route_after_collect,
        {
            "suggest_concepts": "suggest_concepts",
            "wait_for_more_info": "wait_for_more_info"
        }
    )

    graph.add_edge("suggest_concepts", END)
    graph.add_edge("wait_for_more_info", END)
    graph.add_edge("generate", END)

    return graph.compile()