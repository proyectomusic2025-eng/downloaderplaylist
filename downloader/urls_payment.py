from django.urls import path
from . import views_payment as p
urlpatterns = [
    path('webhook/kofi/', p.kofi_webhook, name='kofi_webhook'),
]
