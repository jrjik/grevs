from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Category, Service
from .serializers import CategorySerializer

@api_view(['GET'])
def get_catalog(request):
    """
    Возвращает все категории с вложенными услугами.
    """
    categories = Category.objects.all().order_by('order')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)
