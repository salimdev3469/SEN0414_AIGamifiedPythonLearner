"""
URL configuration for AI Tutor app.
"""
from django.urls import path
from . import views

app_name = 'ai_tutor'

urlpatterns = [
    # Chatbot API endpoints
    path('api/chatbot/send/', views.send_message_view, name='send_message'),
    path('api/chatbot/history/<int:conversation_id>/', views.get_history_view, name='get_history'),
    path('api/chatbot/history/', views.list_conversations_view, name='list_conversations'),
    path('api/chatbot/delete/<int:conversation_id>/', views.delete_conversation_view, name='delete_conversation'),
    path('api/chatbot/new/', views.new_conversation_view, name='new_conversation'),
    path('api/chatbot/context/<str:context_type>/<int:context_id>/', views.context_conversation_view, name='context_conversation'),
    
    # Debug endpoint
    path('api/chatbot/check-api-key/', views.check_api_key_view, name='check_api_key'),
]

