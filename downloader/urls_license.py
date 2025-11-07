from django.urls import path
from . import views_license

urlpatterns = [
    path('api/activate/', views_license.api_activate, name='api_activate'),
    path('api/validate/', views_license.api_validate, name='api_validate'),
]
