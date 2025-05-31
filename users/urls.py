# users/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import UserProfileView, ActivationConfirmView
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('register/', views.register, name='register'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:pk>/', UserProfileView.as_view(), name='user_profile'),
    path('payment/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payment/<int:pk>/approve/', views.approve_payment, name='approve_payment'),
    path('payment/<int:pk>/reject/', views.reject_payment, name='reject_payment'),
    path('payment/export/', views.export_payments, name='export_payments'),

    # Activation URLs
    path('activation-sent/', views.activation_sent, name='activation_sent'),
    path('activate/<uidb64>/<token>/', ActivationConfirmView.as_view(), name='activation_confirm'),
    

    path('contact/', views.contact_view, name='contact'),
    path('messages/<int:message_id>/delete/', views.message_delete, name='message_delete'),

    path('activate-password/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='users/password_set.html',
             success_url='/login/'
         ), name='activate_zpassword'),

    # Dashboard URLs
    path('dashboard/', views.dashboard_redirect, name='dashboard_redirect'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('registrar/dashboard/', views.registrar_dashboard, name='registrar_dashboard'),
    path('transport/dashboard/', views.transport_dashboard, name='transport_dashboard'),
    path('bank/dashboard/', views.bank_dashboard, name='bank_dashboard'),
    path('reservation/<int:pk>/approve/', views.approve_reservation, name='approve_reservation'),
    path('pricing/', views.pricing, name='pricing'),
    path('contact/', views.contact, name='contact'),
    # Password reset URLs
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    path('check-availability/', views.check_availability, name='check_availability'),

    path('user/delete/<int:user_id>/', views.delete_user, name='delete_user'),

     
]
