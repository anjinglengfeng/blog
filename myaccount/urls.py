from django.urls import path
from . import views

app_name = "myaccount"

urlpatterns = [
    path('profile/', views.profile, name="profile"),
    path('profile_update/', views.profile_update, name='profile_update'),
    path('my_post/', views.my_post, name='my_post'),
]