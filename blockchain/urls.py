from django.urls import path
from . import views
from .views import send_message_view, decrypt_message_view,encrypt_message_view, people

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('messages/', views.messages_view, name='messages'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('all_blocks/', views.all_blocks_view, name='all_blocks'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('get_full_json/', views.get_full_json, name='get_full_json'),
    path('send-coins/', views.send_coins_view, name='send_coins'),
    path('add_wallet/', views.add_wallet, name='add_wallet'), 
    path('tasks/', views.tasks_view, name='tasks'),
    path('start/', views.start_script, name='start_script'),
    path('stop/', views.stop_script, name='stop_script'),
    path('get_console_output/', views.get_console_output, name='get_console_output'),
    path('send-message/', send_message_view, name='send_message_view'),
    path('decrypt/', decrypt_message_view, name='decrypt_message'),
    path('encrypt_message/', encrypt_message_view, name='encrypt_message_view'),
    path('people/', people, name='people'),
    ]