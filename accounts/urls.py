from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeDoneView

app_name = 'accounts'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('Profile/', views.account_profile, name='account_profile'),
    path('edit/', views.account_edit, name='account_edit'),
    path("delete/", views.account_delete, name="account_delete"),
    
    path('password/change/', views.AccountPasswordChangeView.as_view(), name='password_change'),
    path('password/change/done/', PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),name='password_change_done'),
]