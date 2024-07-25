import random

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from .permissions import IsSeller, IsCustomer
from django.core.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from django.core.mail import send_mail

from .models import(
    User,
    Item, 
    Order, 
    Profile,
    Cart, 
    CartItem,
    OrderItem,
    Favorite,
    Review,
    SupportRequest,
)

from .serializers import (
    VerificationCodeSerializer, 
    RegisterSerializer, 
    ItemSerializer, 
    OrderSerializer, 
    ProfileSerializer,
    ResendVerificationSerializer,
    CartSerializer, 
    FavoriteSerializer,
    ReviewSerializer,
    SupportRequestSerializer,
)



#random verification code
def generate_verification_code():
    return str(random.randint(100000, 999999))


#sending email
def send_email_verification_code(email, code):
    print(f'Sending email to: {email}')
    print(f'Verification code: {code}')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            verification_code = generate_verification_code()
            user.verification_code = verification_code
            user.save()
            send_email_verification_code(user.email, verification_code)
            return Response({'detail': 'User registered successfully. Please verify your account'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='verify')
    def verify(self, request):
        serializer = VerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            try:
                user = User.objects.get(verification_code=code)
                if user.is_verified:
                    return Response({'detail': 'User already verified.'}, status=status.HTTP_400_BAD_REQUEST)
                user.is_verified = True
                user.verification_code = ''
                user.save()
                return Response({'detail': 'User verified successfully.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'detail': 'Invalid verification code.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='resend-verification')
    def resend_verification(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                if user.is_verified:
                    return Response({'detail': 'User is already verified.'}, status=status.HTTP_400_BAD_REQUEST)
                verification_code = generate_verification_code()
                user.verification_code = verification_code
                user.save()
                send_email_verification_code(user.email, verification_code)
                return Response({'detail': 'Verification code resent successfully.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'detail': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def perform_create(self, serializer):
        if not IsSeller().has_permission(self.request, None):
            raise PermissionDenied('Not authorized')
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        item = self.get_object()
        if not IsSeller().has_permission(self.request, item):
            raise PermissionDenied('Not authorized')
        serializer.save()

    def perform_destroy(self, instance):
        item = self.get_object()
        if not IsSeller().has_permission(self.request, item):
            raise PermissionDenied('Not authorized')
        instance.delete()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='add')
    def add_to_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        item = Item.objects.get(pk=request.data['item_id'])
        quantity = request.data.get('quantity', 1)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        return Response({'detail': 'Item added to cart'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='remove')
    def remove_from_cart(self, request):
        cart = Cart.objects.get(user=request.user)
        item = Item.objects.get(pk=request.data['item_id'])
        cart_item = CartItem.objects.get(cart=cart, item=item)
        cart_item.delete()
        return Response({'detail': 'Item removed from cart'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='create-order')
    def create_order(self, request):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.create(customer=request.user)
        for cart_item in cart.items.all():
            OrderItem.objects.create(order=order, item=cart_item.item, quantity=cart_item.quantity)
        cart.items.all().delete()
        return Response({'detail': 'Order created'}, status=status.HTTP_201_CREATED)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='mark')
    def mark_favorite(self, request, pk=None):
        try:
            item = Item.objects.get(id=pk)
        except Item.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        favorite, created = Favorite.objects.get_or_create(user=request.user, item=item)
        if created:
            return Response({'detail': 'Item marked as favorite'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Item is already marked as favorite'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='unmark')
    def unmark_favorite(self, request, pk=None):
        try:
            item = Item.objects.get(id=pk)
        except Item.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
        favorite = Favorite.objects.filter(user=request.user, item=item).first()
        if favorite:
            favorite.delete()
            return Response({'detail': 'Item unmarked as favorite'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Item was not marked as favorite'}, status=status.HTTP_404_NOT_FOUND)



class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SupportRequestViewSet(viewsets.ModelViewSet):
    serializer_class = SupportRequestSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = SupportRequest.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return SupportRequest.objects.filter(user=user)
        return SupportRequest.objects.none()

    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user, email=self.request.user.email)
    
    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            return Response({'detail': 'Not authorized to update this support request.'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            return Response({'detail': 'Not authorized to delete this support request.'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()
