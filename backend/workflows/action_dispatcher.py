from workflows.intent_priority import Intent
from workflows.agents import (
    agent_b,
    agent_c,
    agent_d,
    agent_e
)

def dispatch_actions(actions: list[dict], session_id: str):
    """
    Xử lý danh sách các hành động đã được gán intent và sắp xếp theo độ ưu tiên.
    Gọi đúng agent xử lý cho từng intent.
    """
    for action in actions:
        intent = action["intent"]
        phrase = action["phrase"]

        match intent:
            case Intent.PROVIDE_INFO:
                agent_b.extract_and_store_info(phrase, session_id)
                agent_c.check_missing_fields(session_id)

            case Intent.REQUEST_CONCEPT:
                agent_d.generate_concepts(session_id)

            case Intent.GENERATE_DEMO:
                agent_e.generate_image_from_selected_concept(phrase, session_id)

            case _:
                print(f"[DISPATCH WARNING] Không xử lý intent: {intent}")
