# employee/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('reserve/', views.reserve_transport, name='reserve_transport'),
    path('my-requisitions/', views.my_requisitions, name='my_requisitions'),
    path('requisition/<int:pk>/', views.requisition_detail, name='requisition_detail'),
]