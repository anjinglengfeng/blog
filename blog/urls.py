from django.urls import path
from . import views
from .feeds import LastestPostFeed
from .views import AddFavView


app_name = 'blog'

urlpatterns = [
    path('',views.post_list, name='post_list'),
    # path('',views.PostListView.as_view(), name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',views.post_detail,name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('tag_list/', views.tag_list, name='tag_list'),
    path('feed/', LastestPostFeed(), name='post_feed'),
    path('links/', views.links, name='links'),
    path('readers/', views.readers, name='readers'),
    path('search/', views.search, name='search'),
    path('add_post/', views.add_post, name='add_post'),
    path('update_post/<int:id>/', views.update_post, name='update_post'),
    path('delete_post/', views.delete_post, name='delete_post'),
    path('add_fav/', AddFavView.as_view(), name="add_fav"),  # 添加机构收藏
]