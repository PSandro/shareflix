from django.urls import path, re_path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login/', views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('profile/', views.profile_change_view, name="profile_change"),
    re_path(r'^.*\.html', views.pages, name='pages')
]
