from workflows.agents.agent_a import split_message_into_phrases
from workflows.agents.agent_intent_parser import analyze_phrases
from workflows.intent_priority import get_intent_priority
from workflows.action_dispatcher import dispatch_actions
from workflows.agents.agent_f import summarize_response

def handle_user_message(message: str, session_id: str) -> dict:
    """
    Agent Router: entry point của hệ thống
    - Gọi Agent A để tách message thành fragments
    - Gửi fragments sang intent parser → action list
    - Sắp xếp theo priority rồi dispatch từng action
    - Nhận kết quả từ Agent F để trả về frontend
    """

    try:
        # B1: Agent A – tách message thành từng ý nhỏ
        fragments = split_message_into_phrases(message)
        if not fragments:
            print("[Agent Router] ⚠️ Không tách được fragments.")
            return {"reply": "Tôi chưa hiểu rõ ý bạn, bạn có thể nói rõ hơn không?", "concepts": None, "image_url": None}

        print("[Debug] Fragments tách ra từ message:")
        for i, f in enumerate(fragments, 1):
            print(f"  {i}. {f}")

        # B2: Gán intent cho từng fragment
        list_action = analyze_phrases(fragments, session_id)
        if not list_action:
            print("[Agent Router] ⚠️ Không gán được intent nào hợp lệ.")
            return {"reply": "Tôi chưa hiểu rõ ý bạn, bạn có thể nói rõ hơn không?", "concepts": None, "image_url": None}

        print("[Debug] Danh sách action:")
        for act in list_action:
            print(f"  - Phrase: {act['phrase']}, Intent: {act['intent']}")

        # B3: Sắp xếp list_action theo priority
        list_action.sort(key=lambda a: get_intent_priority(a["intent"]))

        # B4: Dispatch → agent B/C/D/E xử lý từng intent
        dispatch_results = dispatch_actions(list_action, session_id)

        print("[Debug] dispatch_results:", dispatch_results)

        # B5: Agent F – Tổng hợp phản hồi cuối cùng
        final_response = summarize_response(dispatch_results)

        # B6: Trả kết quả hợp lệ về frontend
        if not isinstance(final_response, dict):
            print("[Agent Router] ⚠️ Agent F không trả về dict.")
            return {
                "reply": "Xin lỗi, hiện tại tôi không thể phản hồi yêu cầu này.",
                "concepts": None,
                "image_url": None
            }

        return final_response

    except Exception as e:
        print("[Agent Router Error]", e)
        return {
            "reply": "Hệ thống gặp lỗi khi xử lý yêu cầu. Vui lòng thử lại sau.",
            "concepts": None,
            "image_url": None
        }
