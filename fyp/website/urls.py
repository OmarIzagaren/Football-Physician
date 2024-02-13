from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('player/', views.player_details, name='player'),
    path('add_injury/', views.injury_details, name='add_injury'),
    path('view_player/edit/<int:injury_id>/', views.edit_injury, name='edit_injury'),
    path('view_player/', views.player_view, name='view_player'),
    path('view_player/get_player_injuries/', views.get_player_injuries, name='get_player_injuries'),
    path('view_player/get_player_details/', views.get_player_details, name='get_player_details'),
    path('view_player/delete_player/', views.delete_player, name='delete_player'),
    path('view_player/edit/<int:id>/delete_injury/', views.delete_injury, name='delete_injury'),
    path('injury_prediction/', views.predict_injury, name='injury_prediction'),
    path('injury_scan_acl/', views.detect_acl, name='injury_scan_acl')
]
