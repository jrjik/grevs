import time
import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import VK_TOKEN, VK_GROUP_ID, API_VERSION, DEFAULT_ANSWER
from states import (
    get_state, set_state, clear_state, 
    is_waiting_manager, is_manager, UserState,
    is_in_conversation, end_conversation, get_active_user, set_active_user,
    get_next_from_queue
)
from faq import get_faq_keyboard, find_answer, get_all_faq
from manager import (
    init_vk_api, forward_to_manager, forward_manager_reply, send_to_user, 
    get_main_keyboard, get_manager_keyboard
)

def handle_message(event, vk_api_instance):
    """Обработка входящего сообщения"""
    user_id = event.user_id
    message = event.text.strip()
    state = get_state(user_id)
    
    print(f"📨 Сообщение от {user_id}: '{message[:50]}...' (состояние: {state})")

    try:
        #если пишет менеджер 
        if is_manager(user_id):
            handle_manager_message(user_id, message, vk_api_instance)
            return

        # юзер ждет ответа менеджера 
        if state == UserState.WAITING_FOR_MANAGER:
            if message.lower() in ('🔙 назад в меню', 'назад', 'меню', 'стоп'):
                clear_state(user_id)
                send_to_user(user_id, '✅ Вы вернулись в главное меню.', vk_api_instance, get_main_keyboard())
                return
            
            if forward_to_manager(user_id, message, vk_api_instance):
                send_to_user(
                    user_id, 
                    '✅ Ваше сообщение передано менеджеру. Ожидайте ответа.\n\n*Напишите "назад" чтобы вернуться в меню.*',
                    vk_api_instance
                )
            return

        # обработка команд главного меню 
        if 'связаться с менеджером' in message.lower() or message.lower() == 'менеджер':
            set_state(user_id, UserState.WAITING_FOR_MANAGER)
            send_to_user(
                user_id,
                '👨‍💼 *Режим связи с менеджером*\n\nНапишите ваше сообщение, и оно будет передано нашему специалисту.',
                vk_api_instance
            )
            return
        
        elif 'часто задаваемые вопросы' in message.lower() or message.lower() in ('вопросы', 'faq', '❓'):
            send_to_user(
                user_id,
                get_all_faq(),
                vk_api_instance,
                get_faq_keyboard()
            )
            return
        
        elif message.lower() in ('меню', 'старт', 'start', '🔙'):
            clear_state(user_id)
            send_to_user(
                user_id,
                '👋 Здравствуйте! Чем могу помочь?\n\nВыберите действие:',
                vk_api_instance,
                get_main_keyboard()
            )
            return
        
        answer = find_answer(message)
        if answer:
            send_to_user(
                user_id,
                answer + '\n\n❓ *Ещё вопрос?* Нажмите на кнопку или напишите свой вопрос.',
                vk_api_instance,
                get_faq_keyboard()
            )
            return

        send_to_user(
            user_id,
            f'🤖 {DEFAULT_ANSWER}\n\nВы можете:\n• Написать "менеджер" для связи со специалистом\n• Написать "вопросы" для просмотра часто задаваемых вопросов ',
            vk_api_instance,
            get_main_keyboard()
        )
        
    except Exception as e:
        print(f"Ошибка в handle_message: {e}")
        import traceback
        traceback.print_exc()

    
def handle_manager_mode(user_id: int, message: str, event, vk_api_instance):
    """Обработка сообщений в режиме менеджера"""
    if 'ответить пользователю' in message:
        send_to_user(
            user_id,
            '✍️ Напишите *ID пользователя* и сообщение в формате:\n`123456: Ваше сообщение`',
            vk_api_instance
        )
        set_state(user_id, UserState.MANAGER_MODE)
        return
    
    if get_state(user_id) == UserState.MANAGER_MODE:
        try:
            # парсим формат 123456
            if ':' in message:
                parts = message.split(':', 1)
                target_id = int(parts[0].strip())
                response_text = parts[1].strip()
                
                send_to_user(
                    target_id,
                    f'👨‍💼 *Ответ от менеджера:*\n\n{response_text}',
                    vk_api_instance
                )
                send_to_user(
                    user_id,
                    f'Собщение отправлено пользователю {target_id}',
                    vk_api_instance,
                    get_manager_keyboard()
                )
                clear_state(user_id)
            else:
                send_to_user(
                    user_id,
                    'Неверный формат. Используйте: `ID: сообщение`',
                    vk_api_instance
                )
        except ValueError:
            send_to_user(
                user_id,
                'не удалось распознать ID пользователя. Попробуйте снова.',
                vk_api_instance
            )
        return

def handle_manager_message(manager_id: int, message: str, vk_api_instance):
    msg_lower = message.lower().strip()

    # команда "следующий клиент"
    if 'следующий' in msg_lower or '⏭️' in msg_lower:
        next_user_id = get_next_from_queue()
        
        if next_user_id:
            set_active_user(manager_id, next_user_id)
            
            # пишем пользователю, что его зовут
            send_to_user(
                next_user_id,
                '🔔 *Ваша очередь пришла!*\nМенеджер готов принять вас. Напишите ваш вопрос.',
                vk_api_instance
            )
            
            # пишем менеджеру, кого взяли
            send_to_user(
                manager_id,
                f'✅ Подключен следующий клиент: {next_user_id}.\nОжидание сообщения от пользователя...',
                vk_api_instance,
                keyboard=json.dumps(get_manager_keyboard(), ensure_ascii=False)
            )
        else:
            send_to_user(
                manager_id,
                '📭 Очередь пуста. Нет ожидающих клиентов.',
                vk_api_instance,
                keyboard=json.dumps(get_manager_keyboard(), ensure_ascii=False)
            )
        return

    # завершить диалог
    if msg_lower in ('завершить', 'стоп', 'конец', '🔚 завершить диалог'):
        ended_user = end_conversation(manager_id) 
        
        if ended_user:
            send_to_user(ended_user, '👋 Диалог завершён. Спасибо за обращение!', vk_api_instance)
            send_to_user(manager_id, f'✅ Диалог с {ended_user} закрыт.', vk_api_instance, keyboard=json.dumps(get_manager_keyboard(has_active_chat=False), ensure_ascii=False))
        else:
            send_to_user(manager_id, 'ℹ️ Нет активного диалога.', vk_api_instance, keyboard=json.dumps(get_manager_keyboard(has_active_chat=False), ensure_ascii=False))
        return

    # обычное сообщение (ответ юзеру)
    current_user = get_active_user(manager_id) 
    if current_user:
        forward_manager_reply(manager_id, message, vk_api_instance)
        return

    # если менеджер пишет в пустоту
    send_to_user(manager_id, '⚠️ У вас нет активного диалога. Нажмите "Следующий клиент" или дождитесь заявки.', vk_api_instance, keyboard=json.dumps(get_manager_keyboard(has_active_chat=False), ensure_ascii=False))

def main():
    """Запуск бота"""
    print('🤖 Запуск VK Bot для "Гревс"...')
    
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk_api_instance = init_vk_api()
    longpoll = VkLongPoll(vk_session)
    
    print('✅ Бот запущен. Ожидание сообщений...')
    
    
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            print(f'📨 Сообщение от {event.user_id}: {event.text}')
            handle_message(event, vk_api_instance)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n🛑 Бот остановлен')
        