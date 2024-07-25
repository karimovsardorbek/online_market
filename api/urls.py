from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenVerifyView
)

from .views import (
    RegisterView, 
    VerifyUserView, 
    LoginView, 
    ItemListCreateView, 
    ItemDetailView, 
    OrderListCreateView, 
    ProfileListCreateView,
    ResendVerificationCodeView,
    OrderDetailView,
    CartDetailView,
    AddToCartView,
    RemoveFromCartView,
    CreateOrderFromCartView,
    MarkFavoriteView,
    UnmarkFavoriteView,
    ListFavoritesView
)



urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify/', VerifyUserView.as_view(), name='verify_user'),
    path('resend-verification-code/', ResendVerificationCodeView.as_view(), name='resend_verification_code'),

    path('items/', ItemListCreateView.as_view(), name='item_list_create'),
    path('items/<int:pk>/', ItemDetailView.as_view(), name='item_detail'),

    path('orders/', OrderListCreateView.as_view(), name='order_list_create'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),

    path('profiles/', ProfileListCreateView.as_view(), name='profile-list-create'),  

    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('cart/checkout/', CreateOrderFromCartView.as_view(), name='create-order-from-cart'),

    path('favorites/', ListFavoritesView.as_view(), name='list-favorites'),
    path('favorites/mark/<int:item_id>/', MarkFavoriteView.as_view(), name='mark-favorite'),
    path('favorites/unmark/<int:item_id>/', UnmarkFavoriteView.as_view(), name='unmark-favorite'),

]


