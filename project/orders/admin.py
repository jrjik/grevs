from django.contrib import admin
from django.utils.html import format_html
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'created_at', 'client_name', 'phone', 'funeral_type', 'autopsy_type', 
        'estimated_total', 'status', 'package_name_display', 'source', 'request_type' 
    )
    list_filter = ('status', 'funeral_type', 'autopsy_type', 'created_at', 'source', 'request_type') 
    search_fields = ('phone', 'client_name')

    readonly_fields = (
        'created_at',
        'estimated_total',
        'selected_services_display',
        'funeral_type',
        'autopsy_type',
        'package_info_display',
        'source',  
        'request_type',  
    )

    list_editable = ('status',)

    fieldsets = (
        ('Клиент', {
            'fields': ('client_name', 'phone', 'created_at')
        }),
        ('Тип услуги', {
            'fields': ('funeral_type', 'autopsy_type')
        }),
        ('Источник заявки', { 
            'fields': ('source', 'request_type'),
            'classes': ('collapse',)  
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
        
        funeral_type = obj.funeral_type
        if funeral_type == 'cremation':
            type_key = 'cremation'
            type_display = 'Кремация'
        else:  # 'new' или 'relative'
            type_key = 'burial'
            type_display = 'Похороны'
        
        package_services = {
            'basic': {
                'burial': [
                    'Оформление документов',
                    'Гроб шестигранный деревянный (обитый тканью)',
                    'Крест эконом',
                    'Табличка пластиковая',
                    'Покрывало в гроб (тюль)',
                    'Копка могилы',
                    'Катафалк стандартный'
                ],
                'cremation': [
                    'Оформление документов',
                    'Гроб шестигранный деревянный (обитый тканью) для кремации',
                    'Урна пластиковая',
                    'Табличка пластиковая',
                    'Покрывало в гроб (тюль)',
                    'Катафалк стандартный',
                    'Кремация',
                    'Место в колумбарии (нижняя часть)'
                ]
            },
            'optimal': {
                'burial': [
                    'Оформление документов',
                    'Гроб шестигранный дерево-лак',
                    'Крест металлический',
                    'Табличка металлическая',
                    'Покрывало в гроб (шелк)',
                    'Копка могилы',
                    'Катафалк стандартный',
                    'Венок средний (1,20 м)',
                    'Выносная группа (короткая, 1 точка)',
                    'Отпевание',
                    'Ограда на могилу'
                ],
                'cremation': [
                    'Оформление документов',
                    'Гроб шестигранный дерево-лак для кремации',
                    'Урна металлическая',
                    'Табличка металлическая',
                    'Покрывало в гроб (шелк)',
                    'Катафалк стандартный',
                    'Кремация',
                    'Венок средний (1,20 м)',
                    'Отпевание',
                    'Место в колумбарии (верхний уровень)'
                ]
            },
            'extended': {
                'burial': [
                    'Оформление документов',
                    'Гроб дубовый',
                    'Крест металлический',
                    'Табличка металлическая',
                    'Покрывало в гроб (стеганое)',
                    'Копка могилы',
                    'Катафалк иномарка',
                    'Венок большой (1,5 м)',
                    'Выносная группа (длинная, 2 точки)',
                    'Отпевание',
                    'Ограда на могилу',
                    'Прощальный зал (батюшка + зал)',
                    'Церковный набор (венчик, молитва, крест нательный, крест в руку, икона)'
                ],
                'cremation': [
                    'Оформление документов',
                    'Гроб четырехгранный двустворчатый лакированный для кремации',
                    'Урна металлическая',
                    'Табличка металлическая',
                    'Покрывало в гроб (стеганое)',
                    'Катафалк иномарка',
                    'Кремация',
                    'Венок большой (1,5 м)',
                    'Отпевание',
                    'Место в колумбарии (на уровне глаз)',
                    'Прощальный зал (батюшка + зал)',
                    'Церковный набор (венчик, молитва, крест нательный, крест в руку, икона)'
                ]
            }
        }
        
        services_list = package_services.get(package_name, {}).get(type_key, [])
        
        result = []
        result.append(f"Пакет: {package_display_names.get(package_name, package_name)}")
        result.append(f"Тип: {type_display}")
        result.append("")
        result.append("Состав пакета:")
        
        for idx, service_name in enumerate(services_list, 1):
            result.append(f"{idx}. {service_name}")
        
        package_prices = {
            'burial': {'basic': 35000, 'optimal': 58000, 'extended': 95000},
            'cremation': {'basic': 28000, 'optimal': 45000, 'extended': 75000}
        }
        
        package_price = package_prices.get(type_key, {}).get(package_name, 0)
        result.append("")
        result.append(f"Стоимость пакета: {package_price} ₽")
        
        return "\n".join(result)
    
    package_info_display.short_description = "Информация о пакете"

    def selected_services_display(self, obj):
        """Простое текстовое отображение выбранных услуг"""
        if not obj.selected_services:
            return "Услуги не выбраны"

        package_name = None
        individual_services = []
        
        for service_id in obj.selected_services:
            if isinstance(service_id, str) and service_id.startswith('package_'):
                package_name = service_id.replace('package_', '')
            else:
                individual_services.append(service_id)
        
        result = []
        
        if package_name:
            package_names = {
                'basic': 'Базовый',
                'optimal': 'Оптимальный',
                'extended': 'Расширенный'
            }
            result.append(f"Выбран пакет: {package_names.get(package_name, package_name)}")
            result.append(f"Подробный состав смотрите в секции выше 'Информация о пакете'")
        
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

    def autopsy_type_display(self, obj):
        """Красивое отображение типа вскрытия"""
        autopsy_types = {
            'queue': 'Очередное (от 8 900 ₽)',
            'same_day': 'В день обращения (от 16 550 ₽)',
            'paid': 'Платное (устаревшее)', 
            'free': 'Бесплатное (устаревшее)'  
        }
        return autopsy_types.get(obj.autopsy_type, obj.autopsy_type)
    
    autopsy_type_display.short_description = "Тип вскрытия"
