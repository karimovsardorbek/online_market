from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from .views import (
    register_view, 
    verify_user_view, 
    login_view, 
    item_list_create_view, 
    item_detail_view, 
    order_list_create_view, 
    profile_list_create_view,
    resend_verification_code_view,
    order_detail_view
)


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('verify/', verify_user_view, name='verify_user'),
    path('items/', item_list_create_view, name='item_list_create'),
    path('items/<int:pk>/', item_detail_view, name='item_detail'),
    path('orders/', order_list_create_view, name='order_list_create'),
    path('orders/<int:pk>/', order_detail_view, name='order_detail'),
    path('profiles/', profile_list_create_view, name='profile-list-create'),
    path('resend-verification-code/', resend_verification_code_view, name='resend_verification_code'),
]


