from django.urls import path
from rest_framework.routers import DefaultRouter


from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView, 
    TokenVerifyView
)

from .views import (
    UserViewSet,
    ItemViewSet,
    OrderViewSet,
    ProfileViewSet,
    CartViewSet,
    FavoriteViewSet,
    ReviewViewSet,
    SupportRequestViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'items', ItemViewSet, basename='item')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'reviews', ReviewViewSet)
router.register(r'support-requests', SupportRequestViewSet)


verification = [
    path("token/", TokenObtainPairView.as_view()),
    path("token/verify", TokenVerifyView.as_view()),
    path("token/refresh", TokenRefreshView.as_view()),
]


urlpatterns = (router.urls + verification)
