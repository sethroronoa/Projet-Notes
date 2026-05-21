from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ajouter/', views.ajouter_ticket, name='ajouter_ticket'),
    path('edit-details/<uuid:pk>/', views.edit_ticket_details, name='edit_ticket_details'),
    path('modifier-statut/', views.modifier_statut, name='modifier_statut'),
    path('supprimer-ticket/', views.supprimer_ticket, name='supprimer_ticket'),
    path('inventaire/', views.inventaire, name='inventaire'),
    path('suivre/', views.suivre_ticket, name='suivre_ticket'),
    path('facture/<uuid:pk>/', views.generer_facture_pdf, name='generer_facture_pdf'),
    path('login/', auth_views.LoginView.as_view(template_name='maintenance/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
