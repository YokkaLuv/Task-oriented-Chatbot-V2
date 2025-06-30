from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from services.openai_service import (
    ask_gpt,
    generate_concepts_from_transcript,
    generate_image_from_data,
    extract_design_data_from_history,
)
from services.prompt_builder import extract_selected_concept_index

class ChatState(TypedDict, total=False):
    message: str
    history: list[dict]
    design_data: dict
    reply: str
    concepts: list[str]
    selected_concept: str
    image_url: Optional[str]

REQUIRED_KEYS = [
    "business", "product", "audience",
    "colors", "style", "contact_information"
]

def collect_message(state: ChatState) -> ChatState:
    print("📍 Phase: COLLECT")

    message = state["message"]
    history = state.get("history", [])
    reply = ask_gpt(history + [{"role": "user", "content": message}])

    updated_history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": reply}
    ]

    extracted_data = extract_design_data_from_history(updated_history)
    print("✅ Extracted design data:", extracted_data)

    return {
        **state,
        "reply": reply,
        "history": updated_history,
        "design_data": extracted_data,
        "concepts": state.get("concepts", []) 
    }

def suggest_concepts(state: ChatState) -> ChatState:
    print("📍 Phase: SUGGEST_CONCEPTS")
    transcript = "\n".join(f"{m['role']}: {m['content']}" for m in state.get("history", []))
    concepts = generate_concepts_from_transcript(transcript)
    print("✨ Generated concepts:", concepts)
    return {**state, "concepts": concepts}

def wait_for_more_info(state: ChatState) -> ChatState:
    print("📍 Phase: WAIT_FOR_MORE_INFO")
    return state

def generate_image(state: ChatState) -> ChatState:
    print("📍 Phase: GENERATE_IMAGE")
    concept = state.get("selected_concept", "")
    image_url = generate_image_from_data({"selected_concept": concept})
    print("🖼️ Generated image URL:", image_url)
    return {**state, "image_url": image_url}

def route_after_collect_all(state: ChatState) -> str:
    print("➡️ Routing logic after COLLECT")

    data = state.get("design_data", {})
    message = state.get("message", "")
    concepts = state.get("concepts", [])

    filled_keys = [k for k in REQUIRED_KEYS if data.get(k)]
    print(f"🔎 Filled design keys: {len(filled_keys)}/{len(REQUIRED_KEYS)}")

    if concepts:
        index = extract_selected_concept_index(message, concepts)
        if index is not None:
            print(f"🎯 User selected concept index: {index}")
            state["selected_concept"] = concepts[index]
            print("🔄 Redirecting to: generate")
            return "generate"

    if len(filled_keys) < len(REQUIRED_KEYS):
        print("🔄 Redirecting to: wait_for_more_info")
        return "wait_for_more_info"

    print("🔄 Redirecting to: suggest_concepts")
    return "suggest_concepts"

def build_graph():
    graph = StateGraph(ChatState)

    graph.add_node("collect", collect_message)
    graph.add_node("suggest_concepts", suggest_concepts)
    graph.add_node("wait_for_more_info", wait_for_more_info)
    graph.add_node("generate", generate_image)

    graph.set_entry_point("collect")

    graph.add_conditional_edges(
        "collect",
        route_after_collect_all,
        {
            "suggest_concepts": "suggest_concepts",
            "wait_for_more_info": "wait_for_more_info",
            "generate": "generate"
        }
    )

    graph.add_edge("suggest_concepts", END)
    graph.add_edge("wait_for_more_info", END)
    graph.add_edge("generate", END)

    return graph.compile()
