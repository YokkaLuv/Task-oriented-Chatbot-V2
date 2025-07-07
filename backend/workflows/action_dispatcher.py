from workflows.intent_priority import Intent
from workflows.agents import (
    agent_b,
    agent_c,
    agent_d,
    agent_e
)
from services.db_service import store_selected_concept

def dispatch_actions(actions: list[dict], session_id: str) -> list[dict]:
    """
    Xử lý danh sách các hành động đã được gán intent và sắp xếp theo độ ưu tiên.
    Gọi đúng agent xử lý cho từng intent.
    """
    results = []

    for action in actions:
        intent = action["intent"]
        phrase = action["phrase"]

        match intent:
            case Intent.PROVIDE_INFO:
                result_b = agent_b.extract_and_store_info(phrase, session_id)
                if result_b is not None:
                    results.append(result_b)

            case Intent.REQUEST_CONCEPT:
                result_d = agent_d.generate_concepts(session_id)
                if result_d is not None:
                    results.append(result_d)

            case Intent.CHOOSE_CONCEPT:
                store_selected_concept(session_id, phrase)
                results.append({"selected_concept": phrase})

            case Intent.GENERATE_DEMO:
                result_e = agent_e.generate_image_from_selected_concept(session_id)
                if result_e is not None:
                    results.append({"image_url": result_e})

            case _:
                print(f"[DISPATCH WARNING] Không xử lý intent: {intent}")

    # ✅ Luôn gọi Agent C sau cùng để kiểm tra các trường còn thiếu
    result_c = agent_c.check_missing_fields(session_id)
    if result_c:
        results.append(result_c)

    return results
