from django.contrib import admin
from django import forms

from .models import Category, Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'order')
    list_editable = ('order',)
    list_filter = ('service_type',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    form = ServiceForm
    list_display = ('name', 'category', 'price', 'is_mandatory', 'applicability')
    list_filter = ('category', 'applicability')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_mandatory')

    fieldsets = (
        ('Основное', {
            'fields': ('name', 'category', 'price', 'is_mandatory', 'applicability')
        }),
        ('Детали', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )
    