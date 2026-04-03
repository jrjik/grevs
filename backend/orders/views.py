from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Lead
import json


@api_view(['POST'])
def submit_lead(request):
    """
    Принимает заявку от калькулятора
    """
    try:
        data = request.data

        # Валидация обязательных полей
        if not data.get('phone'):
            return Response(
                {'status': 'error', 'message': 'Телефон обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not data.get('selected_services') or len(data.get('selected_services', [])) == 0:
            return Response(
                {'status': 'error', 'message': 'Выберите хотя бы одну услугу'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаём заявку
        lead = Lead.objects.create(
            client_name=data.get('client_name', ''),
            phone=data.get('phone', ''),
            funeral_type=data.get('funeral_type', 'new'),
            autopsy_type=data.get('autopsy_type', 'paid'),
            selected_services=data.get('selected_services', []),
            estimated_total=data.get('estimated_total', 0),
            comment=data.get('comment', '')
        )

        return Response(
            {'status': 'success', 'lead_id': lead.id},
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'status': 'error', 'message': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
