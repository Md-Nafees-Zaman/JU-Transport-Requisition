from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_transport, name='add_transport'),
    path('list/', views.transport_list, name='transport_list'),
    path('reservation/<int:reservation_id>/', views.reservation_detail, name='reservation_detail'),
]