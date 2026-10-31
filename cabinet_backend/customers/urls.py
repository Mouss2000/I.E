from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.demo_login), path('logout/', views.demo_logout),
    path('laboratories/', views.laboratories),
    path('accounts/', views.accounts), path('accounts/<int:account_id>/', views.accounts),
    path('accounts/<int:account_id>/reset-password/', views.reset_password),
    path('overview/', views.overview), path('logs/', views.logs),
    path('support/', views.support), path('support/<int:ticket_id>/', views.support),
    path('dentist/orders/', views.dentist_orders),
]
