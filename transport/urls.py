from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_transport, name='add_transport'),
    path('list/', views.transport_list, name='transport_list'),

]
