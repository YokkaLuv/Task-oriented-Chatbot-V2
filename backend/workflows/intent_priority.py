# intent_priority.py

INTENT_PRIORITY_MAP = {
    "provide_info": 1,
    "request_concept": 2,
    "generate_demo": 3
}

def get_intent_priority(intent: str) -> int:
    """
    Trả về mức ưu tiên của intent.
    - provide_info → Ưu tiên cao nhất
    - request_concept → Khi đã có info
    - generate_demo → Chỉ sau khi có concept
    - intent khác → Ưu tiên rất thấp (99)
    """
    return INTENT_PRIORITY_MAP.get(intent, 99)
