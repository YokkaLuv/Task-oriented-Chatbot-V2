from workflows.agents.agent_a import split_message_into_phrases
from workflows.agents.agent_intent_parser import analyze_phrases
from workflows.intent_priority import get_intent_priority
from workflows.action_dispatcher import dispatch_actions
from workflows.agents.agent_f import summarize_response
from services.db_service import append_chatlog
from services.eval_service import evaluate_reply


def handle_user_message(message: str, session_id: str) -> dict:
    """
    Agent Router: entry point của hệ thống
    - Ghi log tin nhắn người dùng
    - Gọi Agent A để tách message thành fragments
    - Gán intent và sắp xếp theo priority
    - Dispatch các intent đến các agent chuyên trách
    - Tổng hợp phản hồi từ Agent F
    - Ghi log phản hồi và đánh giá chất lượng
    """

    try:
        # B0: Ghi lại message người dùng
        append_chatlog(session_id, {"role": "user", "content": message})

        # B1: Agent A – tách message thành từng ý nhỏ
        fragments = split_message_into_phrases(message)
        if not fragments:
            print("[Agent Router] ⚠️ Không tách được fragments.")
            reply = "Tôi chưa hiểu rõ ý bạn, bạn có thể nói rõ hơn không?"
            append_chatlog(session_id, {"role": "assistant", "content": reply})
            return {"reply": reply, "concepts": None, "image_url": None}

        print("[Debug] Fragments tách ra từ message:")
        for i, f in enumerate(fragments, 1):
            print(f"  {i}. {f}")

        # B2: Gán intent cho từng fragment
        list_action = analyze_phrases(fragments, session_id)
        if not list_action:
            print("[Agent Router] ⚠️ Không gán được intent nào hợp lệ.")
            reply = "Tôi chưa hiểu rõ ý bạn, bạn có thể nói rõ hơn không?"
            append_chatlog(session_id, {"role": "assistant", "content": reply})
            return {"reply": reply, "concepts": None, "image_url": None}

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

        # B6: Ghi lại phản hồi vào chatlog và evaluate
        reply_text = final_response.get("reply", "")
        if reply_text:
            append_chatlog(session_id, {"role": "assistant", "content": reply_text})
            evaluate_reply(session_id)

        # B7: Trả kết quả hợp lệ về frontend
        if not isinstance(final_response, dict):
            print("[Agent Router] ⚠️ Agent F không trả về dict.")
            fallback = "Xin lỗi, hiện tại tôi không thể phản hồi yêu cầu này."
            append_chatlog(session_id, {"role": "assistant", "content": fallback})
            return {"reply": fallback, "concepts": None, "image_url": None}

        return final_response

    except Exception as e:
        print("[Agent Router Error]", e)
        reply = "Hệ thống gặp lỗi khi xử lý yêu cầu. Vui lòng thử lại sau."
        append_chatlog(session_id, {"role": "assistant", "content": reply})
        return {"reply": reply, "concepts": None, "image_url": None}
