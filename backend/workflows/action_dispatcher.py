from workflows.intent_priority import Intent
from workflows.agents import (
    agent_b,
    agent_c,
    agent_d,
    agent_e
)

def dispatch_actions(actions: list[dict], session_id: str):
    results = []

    for action in actions:
        intent = action["intent"]
        phrase = action["phrase"]

        match intent:
            case Intent.PROVIDE_INFO:
                result_b = agent_b.extract_and_store_info(phrase, session_id)
                if result_b is not None:
                    results.append(result_b)

                result_c = agent_c.check_missing_fields(session_id)
                if result_c is not None:
                    results.append({"missing_fields": result_c})

            case Intent.REQUEST_CONCEPT:
                result_d = agent_d.generate_concepts(session_id)
                if result_d is not None:
                    results.append({"concepts": result_d})

            case Intent.GENERATE_DEMO:
                result_e = agent_e.generate_image_from_selected_concept(session_id)
                if result_e:
                    results.append(result_e)


            case _:
                print(f"[DISPATCH WARNING] Không xử lý intent: {intent}")
                continue

    return results  # 💥 PHẢI return list

