from decouple import config

VK_TOKEN = config('VK_TOKEN') 
VK_GROUP_ID = config('VK_GROUP_ID')  # ID сообщества 
MANAGER_VK_ID = config('MANAGER_VK_ID')  # ID менеджера

API_VERSION = '5.131'
DEFAULT_ANSWER = 'Спасибо за обращение! Наш менеджер ответит вам в ближайшее время.'
