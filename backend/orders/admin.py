from django.contrib import admin
from django.utils.html import format_html
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'created_at', 'client_name', 'phone', 'funeral_type', 'autopsy_type', 
        'estimated_total', 'status', 'package_name_display'
    )
    list_filter = ('status', 'funeral_type', 'autopsy_type', 'created_at')
    search_fields = ('phone', 'client_name')

    readonly_fields = (
        'created_at',
        'estimated_total',
        'selected_services_display',
        'funeral_type',
        'autopsy_type',
        'package_info_display'
    )

    list_editable = ('status',)

    fieldsets = (
        ('Клиент', {
            'fields': ('client_name', 'phone', 'created_at')
        }),
        ('Тип услуги', {
            'fields': ('funeral_type', 'autopsy_type')
        }),
        ('Пакет услуг', {
            'fields': ('package_info_display',),
        }),
        ('Выбранные услуги', {
            'fields': ('selected_services_display', 'estimated_total')
        }),
        ('Статус', {
            'fields': ('status', 'comment')
        }),
    )

    def package_name_display(self, obj):
        """Отображение названия пакета"""
        # Проверяем selected_services на наличие пакета
        if not obj.selected_services:
            return "—"
        
        for service_id in obj.selected_services:
            if isinstance(service_id, str) and service_id.startswith('package_'):
                package_name = service_id.replace('package_', '')
                package_names = {
                    'basic': 'Базовый',
                    'optimal': 'Оптимальный',
                    'extended': 'Расширенный'
                }
                return package_names.get(package_name, "—")
        
        return "—"
    
    package_name_display.short_description = "Пакет"

    def package_info_display(self, obj):
        """Простое текстовое отображение информации о пакете"""
        # Ищем метку пакета
        if not obj.selected_services:
            return "Пакет не выбран"
        
        package_name = None
        for service_id in obj.selected_services:
            if isinstance(service_id, str) and service_id.startswith('package_'):
                package_name = service_id.replace('package_', '')
                break
        
        if not package_name:
            return "Пакет не выбран"
        
        package_display_names = {
            'basic': 'Базовый пакет',
            'optimal': 'Оптимальный пакет',
            'extended': 'Расширенный пакет'
        }
        
        # Определяем тип похорон (преобразуем в burial/cremation)
        funeral_type = obj.funeral_type
        if funeral_type == 'cremation':
            type_key = 'cremation'
            type_display = 'Кремация'
        else:  # 'new' или 'relative'
            type_key = 'burial'
            type_display = 'Похороны'
        
        # Состав пакетов
        package_services = {
            'basic': {
                'burial': [
                    'Оформление всех документов',
                    'Гроб деревянный',
                    'Крест деревянный',
                    'Табличка пластиковая',
                    'Постель в гроб',
                    'Копка могилы',
                    'Катафалк стандартный'
                ],
                'cremation': [
                    'Оформление всех документов',
                    'Гроб деревянный для кремации',
                    'Урна пластиковая',
                    'Табличка пластиковая',
                    'Постель в гроб',
                    'Катафалк стандартный',
                    'Кремация'
                ]
            },
            'optimal': {
                'burial': [
                    'Оформление всех документов',
                    'Гроб лакированный',
                    'Крест металлический',
                    'Табличка пластиковая',
                    'Постель в гроб',
                    'Копка могилы',
                    'Катафалк стандартный',
                    'Венок стандартный (средний)',
                    'Выносная группа',
                    'Отпевание',
                    'Ограда на могилу'
                ],
                'cremation': [
                    'Оформление всех документов',
                    'Гроб лакированный для кремации',
                    'Урна металлическая',
                    'Табличка пластиковая',
                    'Постель в гроб',
                    'Катафалк стандартный',
                    'Кремация',
                    'Венок стандартный (средний)',
                    'Отпевание',
                    'Место в колумбарии (стандарт)'
                ]
            },
            'extended': {
                'burial': [
                    'Оформление всех документов',
                    'Гроб дубовый двухкрышечный',
                    'Крест дубовый резной',
                    'Табличка металлическая',
                    'Постель в гроб',
                    'Копка могилы',
                    'Катафалк иномарка',
                    'Венок большой',
                    'Выносная группа',
                    'Отпевание',
                    'Ограда на могилу',
                    'Прощальный зал',
                    'Церковный набор'
                ],
                'cremation': [
                    'Оформление всех документов',
                    'Гроб дубовый двухкрышечный для кремации',
                    'Урна керамическая',
                    'Табличка металлическая',
                    'Постель в гроб',
                    'Катафалк иномарка',
                    'Кремация',
                    'Венок большой',
                    'Отпевание',
                    'Место в колумбарии (премиум)',
                    'Прощальный зал',
                    'Церковный набор'
                ]
            }
        }
        
        # Получаем список услуг (используем type_key вместо funeral_type)
        services_list = package_services.get(package_name, {}).get(type_key, [])
        
        # Формируем текст
        result = []
        result.append(f"Пакет: {package_display_names.get(package_name, package_name)}")
        result.append(f"Тип: {type_display}")
        result.append("")
        result.append("Состав пакета:")
        
        for idx, service_name in enumerate(services_list, 1):
            result.append(f"{idx}. {service_name}")
        
        # Добавляем цену (тоже используем type_key)
        package_prices = {
            'burial': {'basic': 35000, 'optimal': 58000, 'extended': 95000},
            'cremation': {'basic': 28000, 'optimal': 45000, 'extended': 75000}
        }
        
        package_price = package_prices.get(type_key, {}).get(package_name, 0)
        result.append("")
        result.append(f"Стоимость пакета: {package_price} ₽")
        
        return "\n".join(result)
        
        # Получаем список услуг
        services_list = package_services.get(package_name, {}).get(funeral_type, [])
        
        # Формируем текст
        result = []
        result.append(f"Пакет: {package_display_names.get(package_name, package_name)}")
        result.append(f"Тип: {type_display}")
        result.append("")
        result.append("Состав пакета:")
        
        for idx, service_name in enumerate(services_list, 1):
            result.append(f"{idx}. {service_name}")
        
        # Добавляем цену
        package_prices = {
            'burial': {'basic': 35000, 'optimal': 58000, 'extended': 95000},
            'cremation': {'basic': 28000, 'optimal': 45000, 'extended': 75000}
        }
        
        package_price = package_prices.get(funeral_type, {}).get(package_name, 0)
        result.append("")
        result.append(f"Стоимость пакета: {package_price} ₽")
        
        return "\n".join(result)
    
    package_info_display.short_description = "Информация о пакете"

    def selected_services_display(self, obj):
        """Простое текстовое отображение выбранных услуг"""
        if not obj.selected_services:
            return "Услуги не выбраны"

        # Проверяем, выбран ли пакет
        package_name = None
        individual_services = []
        
        for service_id in obj.selected_services:
            if isinstance(service_id, str) and service_id.startswith('package_'):
                package_name = service_id.replace('package_', '')
            else:
                individual_services.append(service_id)
        
        result = []
        
        # Если выбран пакет
        if package_name:
            package_names = {
                'basic': 'Базовый',
                'optimal': 'Оптимальный',
                'extended': 'Расширенный'
            }
            result.append(f"Выбран пакет: {package_names.get(package_name, package_name)}")
            result.append(f"Подробный состав смотрите в секции выше 'Информация о пакете'")
        
        # Показываем индивидуальные услуги (если есть)
        if individual_services:
            from services.models import Service
            services = Service.objects.filter(id__in=individual_services)
            
            if services:
                result.append("")
                result.append("Дополнительные услуги (не входят в пакет):")
                for service in services:
                    result.append(f"- {service.name} — {service.price} ₽")
            else:
                result.append(f"Индивидуальные услуги не найдены (ID: {individual_services})")
        
        return "\n".join(result) if result else "Услуги не выбраны"

    selected_services_display.short_description = "Выбранные услуги"
    