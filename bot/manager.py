import json
import vk_api
from vk_api.utils import get_random_id
from config import VK_TOKEN, MANAGER_VK_ID, API_VERSION, DEFAULT_ANSWER
from states import (
    start_conversation, get_conversation_partner, 
    end_conversation, is_in_conversation, get_active_user, set_active_user, add_to_queue
)

def init_vk_api():
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    return vk_session.get_api()


def forward_to_manager(user_id: int, message: str, vk_api_instance) -> bool:
    """Переслать сообщение менеджеру или поставить в очередь"""
    try:
        manager_id = int(MANAGER_VK_ID)
        active_user = get_active_user(manager_id)
        
        # Если менеджер занят, но не этим пользователем -> ставим в очередь
        if active_user and active_user != user_id:
            pos = add_to_queue(user_id)
            send_to_user(
                user_id, 
                f'⏳ Менеджер сейчас занят другим клиентом.\nВы в очереди. Позиция: {pos}\nДождитесь уведомления.',
                vk_api_instance
            )
            return False
            
        set_active_user(manager_id, user_id)
        
        vk_api_instance.messages.send(
            user_id=manager_id,
            message=f"💬 *Пользователь {user_id}*: {message}",
            random_id=get_random_id(),
            keyboard=json.dumps(get_manager_keyboard(), ensure_ascii=False)
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки менеджеру: {e}")
        return False

def forward_manager_reply(manager_id: int, reply_text: str, vk_api_instance) -> bool:
    """Переслать ответ менеджера пользователю"""
    try:
        user_id = get_conversation_partner(manager_id)
        
        if not user_id:
            print(f"⚠️ Менеджер {manager_id} не в активном диалоге")
            return False
        
        # Получаем клавиатуру
        main_kb = get_main_keyboard()
        
        vk_api_instance.messages.send(
            user_id=user_id,
            message=f"👨‍💼 *Ответ от менеджера:*\n\n{reply_text}",
            random_id=get_random_id(),
            keyboard=json.dumps(main_kb, ensure_ascii=False) 
        )
        print(f"✅ Ответ переслан пользователю {user_id}")
        return True
    except Exception as e:
        print(f"Ошибка пересылки ответа: {e}")
        return False

def send_to_user(user_id: int, message: str, vk_api_instance, keyboard: dict = None):
    """Отправить сообщение пользователю"""
    try:
        params = {
            'user_id': int(user_id),
            'message': message,
            'random_id': get_random_id()
        }
        if keyboard:
            params['keyboard'] = json.dumps(keyboard, ensure_ascii=False)
        vk_api_instance.messages.send(**params)
        return True
    except Exception as e:
        print(f"Ошибка отправки пользователю {user_id}: {e}")
        return False

def get_main_keyboard() -> dict:
    """Основная клавиатура"""
    return {
        'one_time': False,
        'inline': False,
        'buttons': [
            [{'action': {'type': 'text', 'label': '📞 Связаться с менеджером', 'payload': None}, 'color': 'primary'}],
            [{'action': {'type': 'text', 'label': '❓ Часто задаваемые вопросы', 'payload': None}, 'color': 'secondary'}]
        ]
    }

def get_manager_keyboard(has_active_chat: bool = True) -> dict:
    """Клавиатура менеджера"""
    buttons = []
    
    if has_active_chat:
        buttons.append([{
            'action': {'type': 'text', 'label': '🔚 Завершить диалог', 'payload': None},
            'color': 'negative'
        }])
    
    # Кнопка "Следующий" нужна всегда, если есть очередь или чтобы проверить её
    buttons.append([{
        'action': {'type': 'text', 'label': '⏭️ Следующий клиент', 'payload': None},
        'color': 'primary'
    }])
    
    return {
        'one_time': False,
        'inline': False,
        'buttons': buttons
    }
