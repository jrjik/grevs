from rest_framework import serializers
from .models import Category, Service

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            'id',
            'name',
            'description',
            'price',
            'is_mandatory',
            'applicability'
        ]

class CategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'order',
            'service_type',
            'selection_type',
            'services'
        ]
        