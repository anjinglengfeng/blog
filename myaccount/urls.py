from django.urls import path
from . import views

app_name = "myaccount"

urlpatterns = [
    path('profile/', views.profile, name="profile"),
    path('profile_update/', views.profile_update, name='profile_update'),
    path('my_post/', views.my_post, name='my_post'),
    path('fav_post/', views.fav_post, name='fav_post'),
]