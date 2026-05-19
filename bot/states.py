from enum import Enum
from typing import Optional
import redis
from decouple import config

# redis
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default=6379, cast=int)
REDIS_DB = config('REDIS_DB', default=0, cast=int)

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    r.ping()
    print("✅ Redis подключен успешно")
except redis.ConnectionError as e:
    print(f"❌ Ошибка подключения к Redis: {e}")
    print("💡 Запустите: docker-compose up -d")
    exit(1)


class UserState(Enum):
    IDLE = 'idle'
    WAITING_FOR_MANAGER = 'waiting_for_manager'
    MANAGER_MODE = 'manager_mode'

# user states
def get_state(user_id: int) -> UserState:
    val = r.get(f"user:state:{user_id}")
    return UserState(val) if val else UserState.IDLE

def set_state(user_id: int, state: UserState):
    r.set(f"user:state:{user_id}", state.value)

def clear_state(user_id: int):
    r.delete(f"user:state:{user_id}")

def is_waiting_manager(user_id: int) -> bool:
    return get_state(user_id) == UserState.WAITING_FOR_MANAGER

def is_manager(user_id: int) -> bool:
    from config import MANAGER_VK_ID
    return str(user_id) == str(MANAGER_VK_ID)

# active dialogs
def get_conversation_partner(manager_id: int) -> Optional[int]:
    """Получить ID пользователя, с которым говорит менеджер"""
    val = r.hget("active_chats", str(manager_id))
    return int(val) if val else None

def get_active_user(manager_id: int) -> Optional[int]:
    """Кто сейчас говорит с менеджером """
    return get_conversation_partner(manager_id)

def set_active_user(manager_id: int, user_id: int):
    """Назначить пользователя для диалога"""
    r.hset("active_chats", str(manager_id), str(user_id))
    set_state(user_id, UserState.WAITING_FOR_MANAGER)

def start_conversation(manager_id: int, user_id: int):
    """Начать диалог: менеджер отвечает пользователю"""
    set_active_user(manager_id, user_id)
    print(f"💬 Начат диалог: менеджер {manager_id} ↔ пользователь {user_id}")

def end_conversation(manager_id: int) -> Optional[int]:
    """Завершить диалог и полностью сбросить состояния"""
    user_id = r.hget("active_chats", str(manager_id))
    if user_id:
        r.hdel("active_chats", str(manager_id))
        clear_state(int(user_id))
        print(f"✅ Завершён диалог: менеджер {manager_id} ↔ пользователь {user_id}")
        return int(user_id)
    return None

def is_in_conversation(manager_id: int) -> bool:
    """Проверить, ведёт ли менеджер активный диалог"""
    return r.hexists("active_chats", str(manager_id))

# queue
def add_to_queue(user_id: int) -> int:
    """Добавить в очередь. Возвращает позицию (1, 2, 3...)"""
    if not r.lpos("waiting_queue", str(user_id)):
        r.rpush("waiting_queue", str(user_id))
        set_state(user_id, UserState.WAITING_FOR_MANAGER)
    return r.llen("waiting_queue")

def get_next_from_queue() -> Optional[int]:
    """Взять следующего из очереди"""
    val = r.lpop("waiting_queue")
    if val:
        clear_state(int(val))
        return int(val)
    return None

def get_queue_size() -> int:
    """Длина очереди"""
    return r.llen("waiting_queue")

def is_in_queue(user_id: int) -> bool:
    """Проверить, есть ли пользователь в очереди"""
    return bool(r.lpos("waiting_queue", str(user_id)))
