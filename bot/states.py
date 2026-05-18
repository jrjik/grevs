from enum import Enum
from typing import Dict, Optional
from collections import deque

class UserState(Enum):
    """Возможные состояния пользователя"""
    IDLE = 'idle'                    # Обычный режим
    WAITING_FOR_MANAGER = 'waiting_for_manager'  # Ждёт ответа менеджера
    MANAGER_MODE = 'manager_mode'    # Режим менеджера (для админа)

#TODO: redis
_user_states: Dict[int, UserState] = {}

_active_conversations: Dict[int, int] = {}  

_waiting_queue: deque = deque()
def get_state(user_id: int) -> UserState:
    """Получить состояние пользователя"""
    return _user_states.get(user_id, UserState.IDLE)

def set_state(user_id: int, state: UserState):
    """Установить состояние пользователя"""
    _user_states[user_id] = state

def clear_state(user_id: int):
    """Сбросить состояние пользователя"""
    if user_id in _user_states:
        del _user_states[user_id]

def is_waiting_manager(user_id: int) -> bool:
    """Проверить, ждёт ли пользователь ответа менеджера"""
    return get_state(user_id) == UserState.WAITING_FOR_MANAGER

def is_manager(user_id: int) -> bool:
    """Проверить, является ли пользователь менеджером"""
    from config import MANAGER_VK_ID
    return str(user_id) == str(MANAGER_VK_ID)

def start_conversation(manager_id: int, user_id: int):
    """Начать диалог: менеджер отвечает пользователю"""
    _active_conversations[manager_id] = user_id
    print(f"💬 Начат диалог: менеджер {manager_id} ↔ пользователь {user_id}")

def get_conversation_partner(manager_id: int) -> Optional[int]:
    """Получить ID пользователя, с которым говорит менеджер"""
    return _active_conversations.get(manager_id)

def end_conversation(manager_id: int):
    """Завершить диалог и полностью сбросить состояния"""
    if manager_id in _active_conversations:
        user_id = _active_conversations.pop(manager_id)
        
        clear_state(user_id)        
        print(f"✅ Завершён диалог: менеджер {manager_id} ↔ пользователь {user_id}")
        return user_id
    return None

def is_in_conversation(manager_id: int) -> bool:
    """Проверить, ведёт ли менеджер активный диалог"""
    return manager_id in _active_conversations

def get_state(user_id: int) -> UserState:
    return _user_states.get(user_id, UserState.IDLE)

def set_state(user_id: int, state: UserState):
    _user_states[user_id] = state

def clear_state(user_id: int):
    if user_id in _user_states:
        del _user_states[user_id]

def is_manager(user_id: int) -> bool:
    from config import MANAGER_VK_ID
    return str(user_id) == str(MANAGER_VK_ID)

# === Управление активным диалогом ===

def get_active_user(manager_id: int) -> Optional[int]:
    """Кто сейчас говорит с менеджером"""
    return _active_conversations.get(manager_id)

def set_active_user(manager_id: int, user_id: int):
    """Назначить пользователя для диалога"""
    _active_conversations[manager_id] = user_id

def end_conversation(manager_id: int) -> Optional[int]:
    """Завершить текущий диалог"""
    user_id = _active_conversations.pop(manager_id, None)
    if user_id:
        clear_state(user_id)
    return user_id

# === Управление очередью ===

def add_to_queue(user_id: int) -> int:
    """Добавить в очередь. Возвращает позицию (1, 2, 3...)"""
    if user_id not in _waiting_queue:
        _waiting_queue.append(user_id)
        set_state(user_id, UserState.WAITING_FOR_MANAGER)
    return list(_waiting_queue).index(user_id) + 1

def get_next_from_queue() -> Optional[int]:
    """Взять следующего из очереди"""
    if _waiting_queue:
        user_id = _waiting_queue.popleft()
        return user_id
    return None

def get_queue_size() -> int:
    return len(_waiting_queue)

def is_in_queue(user_id: int) -> bool:
    return user_id in _waiting_queue
