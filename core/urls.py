from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path("", views.home, name="home"),
    path('login/', views.user_login, name="user_login"),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]