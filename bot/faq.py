from typing import Optional 

FAQ_ITEMS = [
    {
        'question': 'Как быстро вы можете приехать?',
        'answer': 'Наш агент может выехать к вам в течение часа после звонка, в любое время суток.'
    },
    {
        'question': 'Какие документы нужны для организации похорон?',
        'answer': 'Паспорт покойного, свидетельство о смерти. Все остальные документы мы поможем оформить.'
    },
    {
        'question': 'Можно ли организовать похороны в кредит?',
        'answer': 'Да, мы работаем с несколькими банками и можем предложить различные варианты рассрочки.'
    },
    {
        'question': 'Организуете ли вы поминальные обеды?',
        'answer': 'Да, мы можем организовать поминальную трапезу в кафе или ресторане, порекомендовать соответствующие места.'
    },
    {
        'question': 'Работаете ли вы круглосуточно?',
        'answer': 'Да, мы работаем 24/7 без выходных и праздников.'
    },
    {
        'question': 'Какие способы оплаты вы принимаете?',
        'answer': 'Мы принимаем наличные, банковские карты и безналичный расчёт.'
    }
]

def get_faq_keyboard() -> dict:
    """Клавиатура только с кнопкой возврата (без вопросов)"""
    return {
        'one_time': False,
        'inline': False,
        'buttons': [
            [{
                'action': {'type': 'text', 'payload': None, 'label': '🔙 Назад в меню'},
                'color': 'negative'
            }]
        ]
    }

def find_answer(question: str) -> Optional[str]:
    """Найти ответ на вопрос (нечёткое совпадение)"""
    question_lower = question.lower().strip()
    
    for item in FAQ_ITEMS:
        if item['question'].lower() in question_lower or question_lower in item['question'].lower():
            return f"❓ *{item['question']}*\n\n✅ {item['answer']}"
    
    return None

def get_all_faq() -> str:
    """Вернуть все вопросы и ответы текстом"""
    result = "📋 *Часто задаваемые вопросы:*\n\n"
    for i, item in enumerate(FAQ_ITEMS, 1):
        result += f"{i}. {item['question']}\n   ↳ {item['answer']}\n\n"
    return result.strip()
    