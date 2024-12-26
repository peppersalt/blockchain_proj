# users/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),  # страница авторизации
    path('register/', views.register_view, name='register'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    # другие URL
]
