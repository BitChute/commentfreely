from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard),
    path('comments', views.comments),
    path('moderation', views.moderation),
    path('users', views.users),
    path('reports', views.reports),
    path('code', views.code),
    path('settings', views.settings),
    path('demo', views.demo),
    
    path('new_site', views.new_site),
    path('new_board', views.new_board),
    
    path('get_user_sites', views.get_user_sites),
    path('delete_user_site', views.delete_user_site),
    path('delete_user_board', views.delete_user_board),
    path('get_user_boards', views.get_user_boards),
    path('get_site_comments', views.get_site_comments),
    path('get_site_users', views.get_site_users),
    path('get_my_comments', views.get_my_comments),
]
