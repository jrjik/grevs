import pytest
from decimal import Decimal
from orders.models import Lead
from django.utils import timezone


@pytest.mark.django_db
class TestLeadModel:

    def test_lead_creation(self):
        """Проверка создания заявки"""
        lead = Lead.objects.create(
            client_name='Тестовый Клиент',
            phone='79991234567',
            funeral_type='cremation',
            autopsy_type='free',
            estimated_total=Decimal('28000.00'),
            comment='Тестовая заявка'
        )
        
        assert lead.id is not None
        assert lead.created_at is not None
        assert lead.status == 'new'
        assert str(lead) == f"Заявка #{lead.id} - 79991234567"

    def test_lead_with_package(self):
        """Проверка заявки с выбранным пакетом"""
        lead = Lead.objects.create(
            client_name='Пакетный Клиент',
            phone='79991234568',
            funeral_type='new',
            selected_services=['package_optimal'],
            estimated_total=Decimal('58000.00')
        )
        
        assert 'package_optimal' in lead.selected_services
        assert lead.estimated_total == Decimal('58000.00')

    def test_lead_filtering_by_status(self):
        """Проверка фильтрации заявок по статусу"""
        Lead.objects.bulk_create([
            Lead(client_name='Клиент 1', phone='79991111111', status='new'),
            Lead(client_name='Клиент 2', phone='79992222222', status='contacted'),
            Lead(client_name='Клиент 3', phone='79993333333', status='closed'),
        ])
        
        new_leads = Lead.objects.filter(status='new')
        assert new_leads.count() == 1
        assert new_leads.first().client_name == 'Клиент 1'

    def test_lead_filtering_by_source(self):
        """Проверка фильтрации по источнику заявки"""
        Lead.objects.bulk_create([
            Lead(client_name='Калькулятор', phone='79994444444', source='calculator'),
            Lead(client_name='Контакты', phone='79995555555', source='contacts'),
        ])
        
        calc_leads = Lead.objects.filter(source='calculator')
        assert calc_leads.count() == 1
        assert calc_leads.first().client_name == 'Калькулятор'

    def test_lead_ordering_by_created_at(self):
        """Проверка сортировки заявок по дате создания"""
        from django.utils import timezone
        import time
        
        lead1 = Lead.objects.create(client_name='Первый', phone='79996666666')
        time.sleep(0.01)  
        lead2 = Lead.objects.create(client_name='Второй', phone='79997777777')
        
        latest_leads = Lead.objects.all()[:2]
        assert latest_leads[0].client_name == 'Второй'  
        assert latest_leads[1].client_name == 'Первый'
