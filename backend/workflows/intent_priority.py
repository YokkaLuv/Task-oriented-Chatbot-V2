from enum import Enum

# Định nghĩa Enum cho intent
class Intent(str, Enum):
    PROVIDE_INFO = "provide_info"
    REMOVE_INFO = "remove_info"
    REQUEST_CONCEPT = "request_concept"
    CHOOSE_CONCEPT = "choose_concept"
    GENERATE_DEMO = "generate_demo"
    UNKNOWN = "unknown"

# Ánh xạ mức độ ưu tiên cho từng intent (càng nhỏ càng xử lý trước)
INTENT_PRIORITY_MAP = {
    Intent.PROVIDE_INFO: 1,
    Intent.REMOVE_INFO: 2,
    Intent.REQUEST_CONCEPT: 3,
    Intent.CHOOSE_CONCEPT: 4,
    Intent.GENERATE_DEMO: 5,
}

def get_intent_priority(intent: str | Intent) -> int:
    """
    Trả về độ ưu tiên xử lý của một intent.
    Nếu không xác định → trả 99 (ưu tiên thấp nhất).
    """
    try:
        # Nếu là string → convert sang Enum
        intent_enum = Intent(intent)
    except ValueError:
        return 99

    return INTENT_PRIORITY_MAP.get(intent_enum, 99)
