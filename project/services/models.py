from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    SERVICE_TYPES = (
        ('funeral', 'Ритуальные услуги (Захоронение)'),
        ('cremation', 'Кремация'),
        ('common', 'Общее (для всех)'),
    )
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='common')

    SELECTION_TYPES = (
        ('single', 'Одиночный выбор (radio)'),
        ('multiple', 'Множественный выбор (checkbox)'),
    )
    selection_type = models.CharField(max_length=10, choices=SELECTION_TYPES, default='multiple')

    class Meta:
        ordering = ['order']
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    is_mandatory = models.BooleanField(default=False, verbose_name="Обязательно")

    APPLICABILITY = (
        ('all', 'Для всех'),
        ('funeral', 'Захоронение (новая + подзахоронение)'),
        ('cremation', 'Только кремация'),
    )

    applicability = models.CharField(max_length=20, choices=APPLICABILITY, default='all')

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return f"{self.name} - {self.price}"
    