from django.urls import path
from . import views

urlpatterns = [
    path('reserve/', views.reserve_transport, name='reserve_transport'),
]
