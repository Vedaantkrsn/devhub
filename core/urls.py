from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path("", views.home, name="home"),
    path('login/', views.user_login, name="user_login"),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('new_project/', views.new_project, name="new_project"),
    path("project/<int:pk>/", views.project_detail, name="project_detail"),
    path("project/<int:pk>/edit/", views.project_edit, name="project_edit"),
    path("project/<int:pk>/delete/", views.project_delete, name="project_delete"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("profile/<str:username>/", views.profile_page, name="profile_page"),
    path("project/<int:pk>/like/", views.like, name="like"),
    path("project/<int:pk>/bookmark/", views.bookmark, name="bookmark"),
]