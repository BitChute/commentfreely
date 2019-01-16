from django.urls import path
from . import api_views

urlpatterns = [
    path('get_comments/<site_id>/<board_id>/<thread_id>', api_views.get_comments, name='get_comments'),
    path('post_comment/<site_id>/<board_id>/<thread_id>', api_views.post_comment, name='post_comment'),
    path('put_comment/<site_id>/<board_id>/<thread_id>', api_views.put_comment, name='put_comment'),
    path('upvote_comment/<site_id>/<board_id>/<thread_id>', api_views.upvote_comment, name='upvote_comment'),
    path('delete_comment/<site_id>/<board_id>/<thread_id>', api_views.delete_comment, name='delete_comment'),
]
