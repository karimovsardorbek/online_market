from django.urls import path, include
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
    path('api/auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', register_view, name='register'),
    path('api/login/', login_view, name='login'),
    path('api/verify/', verify_user_view, name='verify_user'),
    path('api/items/', item_list_create_view, name='item_list_create'),
    path('api/items/<int:pk>/', item_detail_view, name='item_detail'),
    path('api/orders/', order_list_create_view, name='order_list_create'),
    path('api/orders/<int:pk>/', order_detail_view, name='order_detail'),
    path('api/profiles/', profile_list_create_view, name='profile-list-create'),
    path('api/resend-verification-code/', resend_verification_code_view, name='resend_verification_code'),
]


