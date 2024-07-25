import random

from rest_framework.views import APIView
from rest_framework import status, generics, mixins
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsSeller, IsCustomer

from .models import(
    User,
    Item, 
    Order, 
    Profile,
    Cart, 
    CartItem,
    OrderItem,
    Favorite
)

from .serializers import (
    VerificationCodeSerializer, 
    RegisterSerializer, 
    LoginSerializer, 
    ItemSerializer, 
    OrderSerializer, 
    ProfileSerializer,
    ResendVerificationSerializer,
    CartSerializer, 
    CartItemSerializer,
    FavoriteSerializer,
)



#random verification code
def generate_verification_code():
    return str(random.randint(100000, 999999))


#sending email
def send_email_verification_code(email, code):
    print(f'Sending email to: {email}')
    print(f'Verification code: {code}')


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        verification_code = generate_verification_code()
        user.verification_code = verification_code
        user.save()
        send_email_verification_code(user.email, verification_code)


class VerifyUserView(APIView):
    def post(self, request):
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


class ResendVerificationCodeView(APIView):
    def post(self, request):
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


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = User.objects.filter(email=serializer.validated_data['email']).first()
            if user:
                if not user.is_verified:
                    return Response({'error': 'Verify your email first.'}, status=status.HTTP_400_BAD_REQUEST)
                if user.check_password(serializer.validated_data['password']):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        if not IsSeller().has_permission(request, None):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def put(self, request, *args, **kwargs):
        item = self.get_object()
        if not IsSeller().has_permission(request, item):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        item = self.get_object()
        if not IsSeller().has_permission(request, item):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        item = self.get_object()
        if not IsSeller().has_permission(request, item):
            return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


class ProfileListCreateView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# class ProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Profile.objects.all()
#     serializer_class = ProfileSerializer
#     permission_classes = [IsAuthenticated]


class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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


class RemoveFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        item = Item.objects.get(pk=request.data['item_id'])
        cart_item = CartItem.objects.get(cart=cart, item=item)
        cart_item.delete()
        return Response({'detail': 'Item removed from cart'}, status=status.HTTP_200_OK)


class CreateOrderFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(customer=request.user)
        for cart_item in cart.items.all():
            OrderItem.objects.create(order=order, item=cart_item.item, quantity=cart_item.quantity)
        cart.items.all().delete()
        return Response({'detail': 'Order created'}, status=status.HTTP_201_CREATED)



class MarkFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, item_id):
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=request.user, item=item)
        if created:
            return Response({'detail': 'Item marked as favorite'}, status=status.HTTP_201_CREATED)
        return Response({'detail': 'Item is already marked as favorite'}, status=status.HTTP_200_OK)


class UnmarkFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({'detail': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        favorite = Favorite.objects.filter(user=request.user, item=item).first()
        if favorite:
            favorite.delete()
            return Response({'detail': 'Item unmarked as favorite'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Item was not marked as favorite'}, status=status.HTTP_404_NOT_FOUND)


class ListFavoritesView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
