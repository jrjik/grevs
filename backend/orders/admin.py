from django.contrib import admin
from django.utils.html import format_html
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = (
    'id', 'created_at', 'client_name', 'phone', 'funeral_type', 'autopsy_type', 'estimated_total',
    'status')
    list_filter = ('status', 'funeral_type', 'autopsy_type', 'created_at')
    search_fields = ('phone', 'client_name')

    readonly_fields = (
        'created_at',
        'estimated_total',
        'selected_services_display',
        'funeral_type',
        'autopsy_type'
    )

    list_editable = ('status',)

    fieldsets = (
        ('Клиент', {
            'fields': ('client_name', 'phone', 'created_at')
        }),
        ('Тип услуги', {
            'fields': ('funeral_type', 'autopsy_type')
        }),
        ('Выбранные услуги', {
            'fields': ('selected_services_display', 'estimated_total')
        }),
        ('Статус', {
            'fields': ('status', 'comment')
        }),
    )

    def selected_services_display(self, obj):
        if not obj.selected_services:
            return format_html('<span style="color: #999;">Услуги не выбраны</span>')

        from services.models import Service
        services = Service.objects.filter(id__in=obj.selected_services)

        if not services:
            return format_html(
                f'<span style="color: #dc3545;">Услуги не найдены (ID: {obj.selected_services})</span>'
            )

        html = '<ul style="margin: 10px 0; padding-left: 20px;">'
        for service in services:
            html += f'<li style="margin-bottom: 8px;">{service.name} — <strong>{service.price} ₽</strong></li>'
        html += '</ul>'

        return format_html(html)

    selected_services_display.short_description = "Выбранные услуги"
