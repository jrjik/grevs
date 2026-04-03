from django.db import models
from services.models import Service  # Импортируем Service


class Lead(models.Model):
    FUNERAL_TYPES = (
        ('new', 'Новая могила'),
        ('relative', 'Подзахоронение'),
        ('cremation', 'Кремация'),
    )

    AUTOPSY_TYPES = (
        ('paid', 'Платное вскрытие (1-2 дня)'),
        ('free', 'Бесплатное вскрытие (2-3 дня)'),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    client_name = models.CharField(max_length=100, blank=True, verbose_name="Имя клиента")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    funeral_type = models.CharField(max_length=20, choices=FUNERAL_TYPES, verbose_name="Тип услуги")
    autopsy_type = models.CharField(max_length=10, choices=AUTOPSY_TYPES, default='paid',
                                    verbose_name="Вскрытие")

    selected_services = models.JSONField(default=list, verbose_name="Выбранные услуги (ID)")
    estimated_total = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          verbose_name="Сумма (ориентир)")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    STATUS_CHOICES = (
        ('new', 'Новая'),
        ('contacted', 'Связались'),
        ('meeting', 'Встреча назначена'),
        ('closed', 'Завершена'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"Заявка #{self.id} - {self.phone}"

    def get_selected_services_list(self):
        """
        Возвращает список выбранных услуг с названиями и ценами
        """
        if not self.selected_services:
            return "Услуги не выбраны"

        services = Service.objects.filter(id__in=self.selected_services)
        result = []
        for service in services:
            result.append(f"{service.name} — {service.price} ₽")

        if not result:
            return "Услуги не найдены (возможно, были удалены)"

        return "\n".join(result)

    get_selected_services_list.short_description = "Выбранные услуги"

