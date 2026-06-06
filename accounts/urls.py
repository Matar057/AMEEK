from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('admin/users/', views.AdminUserManagementView.as_view(), name='admin_users'),
    path('admin/users/<int:user_id>/toggle/', views.ToggleAdminView.as_view(), name='toggle_admin'),
]
