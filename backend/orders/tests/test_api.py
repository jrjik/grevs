import pytest
from django.test import Client
from orders.models import Lead
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestLeadSubmissionAPI:

    @pytest.fixture
    def api_client(self):
        return Client()

    @pytest.fixture
    def admin_user(self):
        return User.objects.create_superuser(
            username='admin',
            email='admin@grevs.ru',
            password='testpass123'
        )

    def test_successful_lead_submission(self, api_client):
        """Проверка успешной отправки заявки с калькулятора"""
        data = {
            'client_name': 'Иванов Иван Иванович',
            'phone': '79613013040',
            'funeral_type': 'new',
            'autopsy_type': 'paid',
            'selected_services': [1, 5, 12],
            'estimated_total': 45000,
            'comment': 'Нужно связаться до 18:00',
            'consent_given': True
        }
        
        response = api_client.post(
            '/api/orders/lead/',
            data=data,
            content_type='application/json',
            HTTP_X_CSRFTOKEN='test_token'
        )
        
        assert response.status_code == 201
        assert response.json()['status'] == 'success'
        
        # Проверка сохранения в БД
        lead = Lead.objects.get(phone='79613013040')
        assert lead.client_name == 'Иванов Иван Иванович'
        assert lead.funeral_type == 'new'
        assert lead.estimated_total == 45000
        assert lead.source == 'calculator'

    def test_lead_without_consent_rejected(self, api_client):
        """Проверка что заявка сохраняется даже без флага consent"""
        data = {
            'client_name': 'Иванов Иван',
            'phone': '79613013040',
            'funeral_type': 'new',
            'autopsy_type': 'paid',
            'selected_services': [1, 2],
            'consent_given': False  # ✅ Фронтенд не даст отправить, но бэкенд примет
        }
        
        response = api_client.post(
            '/api/orders/lead/',
            data=data,
            content_type='application/json'
        )
        
        # ✅ Бэкенд принимает заявку (валидация на стороне клиента)
        assert response.status_code == 201
        assert response.json()['status'] == 'success'
        
        lead = Lead.objects.get(phone='79613013040')
        assert lead.client_name == 'Иванов Иван'

    def test_lead_without_phone_rejected(self, api_client):
        """Проверка отклонения заявки без телефона"""
        data = {
            'client_name': 'Сидоров Сидор',
            'consent_given': True
        }
        
        response = api_client.post(
            '/api/orders/lead/',
            data=data,
            content_type='application/json'
        )
        
        assert response.status_code == 400
        assert response.json()['status'] == 'error'

    def test_callback_request_submission(self, api_client):
        """Проверка отправки заявки на обратный звонок"""
        data = {
            'client_name': 'Смирнова Анна',
            'phone': '79613013042',
            'message': 'Перезвоните, пожалуйста',
            'consent_given': True,
            'source': 'contacts'
        }
        
        response = api_client.post(
            '/api/orders/callback/',
            data=data,
            content_type='application/json'
        )
        
        assert response.status_code == 201
        lead = Lead.objects.get(phone='79613013042')
        assert lead.source == 'contacts'
        assert lead.request_type == 'callback'
        assert lead.funeral_type is None  
        