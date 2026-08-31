from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('login/', views.LoginView.as_view(), name='auth_login'),
    path('social-login/', views.SocialLoginView.as_view(), name='auth_social_login'),
    path('logout/', views.LogoutView.as_view(), name='auth_logout'),
    path('profile/', views.ProfileView.as_view(), name='auth_profile'),
    path('profile/avatar/', views.AvatarUploadView.as_view(), name='auth_avatar_upload'),
    path('change-password/', views.ChangePasswordView.as_view(), name='auth_change_password'),
    path('forgot-password/', views.ForgotPasswordView.as_view(), name='auth_forgot_password'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='auth_reset_password'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='auth_delete_account'),

    # Admin
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/users/<int:pk>/balance/', views.adjust_balance, name='admin_adjust_balance'),
]
