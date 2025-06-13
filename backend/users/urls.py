from .views import *
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='register_user'),
    path('login/admin/', SuperAdminLoginView.as_view(), name='superadmin_login'),
    path('login/manager/', ManagerLoginView.as_view(), name='manager_login'),
    path('login/cashier/', CashierLoginView.as_view(), name='cashier_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset/', PasswordResetRequest.as_view(), name='pwd_reset'),
    path('reset/confirm/',
         PasswordResetConfirm.as_view(), name='pwd_reset_cofirm'),
    path('change-password/', ChangePasswordView.as_view(),
         name='change-password'),
]