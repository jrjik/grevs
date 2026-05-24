"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from pages import views
from decouple import config
from django.contrib.sitemaps.views import sitemap 
from sitemap import StaticSitemap

ADMIN_URL = config('ADMIN_URL', 'admin')

sitemaps = {
    'static': StaticSitemap,
}

urlpatterns = [
    path(f'{ADMIN_URL}/', admin.site.urls),
    path('', include('services.urls')),
    path('api/', include('services.urls')),
    path('api/orders/', include('orders.urls')),
    path('', views.index, name='index'),
    path('contacts/', views.contacts, name='contacts'),
    path('calculator/', views.calculator, name='calculator'),
    path('services/', views.services, name='services'),
    path('privacy/', views.privacy, name='privacy'),
    path('', lambda r: None, name='home'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
 