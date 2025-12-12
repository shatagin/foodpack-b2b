from django.urls import path, include
from core import views

urlpatterns = [
    path('', include('core.urls')),
]
