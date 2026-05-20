from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Lead
import json
import re


@api_view(['POST'])
def submit_lead(request):
    """
    Принимает заявку от калькулятора
    """
    try:
        data = request.data

        # валидация
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
        
@api_view(['POST'])
def submit_callback(request):
    """
    Принимает заявку на обратный звонок
    """
    try:
        data = request.data

        if not data.get('phone'):
            return Response(
                {'status': 'error', 'message': 'Телефон обязателен'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not data.get('consent_given'):
            return Response(
                {'status': 'error', 'message': 'Необходимо согласие на обработку персональных данных'},
                status=status.HTTP_400_BAD_REQUEST
            )

        lead = Lead.objects.create(
            client_name=data.get('client_name', '').strip(),
            phone=re.sub(r'\D', '', data.get('phone', '')), 
            comment=data.get('message', '').strip(),
            source=data.get('source', 'contacts'),
            request_type='callback',
            funeral_type=None,      
            autopsy_type=None,      
            selected_services=[],
            estimated_total=0,
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

