"""
URL configuration for Gamification app.
"""
from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    # Badge URLs
    path('badges/', views.badges_view, name='badges'),
    
    # Challenge URLs
    path('challenges/', views.challenges_view, name='challenges'),
    
    # Friend URLs
    path('friends/', views.friends_view, name='friends'),
    path('friends/search/', views.friend_search_view, name='friend_search'),
    path('friends/request/<int:user_id>/', views.send_friend_request_view, name='send_friend_request'),
    path('friends/accept/<int:user_id>/', views.accept_friend_request_view, name='accept_friend_request'),
    path('friends/reject/<int:user_id>/', views.reject_friend_request_view, name='reject_friend_request'),
    path('friends/remove/<int:user_id>/', views.remove_friend_view, name='remove_friend'),
    
    # Profile URLs
    path('profile/<str:username>/', views.user_profile_view, name='user_profile'),
]

