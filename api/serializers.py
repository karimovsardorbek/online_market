from rest_framework import serializers


from .models import(
    Profile, 
    Order,
    Item, 
    OrderItem,
    CartItem,
    Cart,
    User,
    Favorite,
    Review,
    SupportRequest,
)


#user serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_seller']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


#verification serializer
class VerificationCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6)


#resending verification code serializer
class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


#register serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_seller', 'full_name']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


#login serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


#profile serializer
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'full_name']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user
        profile = Profile.objects.create(user=user, **validated_data)
        return profile
    

class OrderItemSerializer(serializers.ModelSerializer):
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all())
    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'quantity']
        read_only_fields = ['id', 'order']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)  # Use the related name here

    class Meta:
        model = Order
        fields = ['id', 'customer', 'order_items', 'created_at']
        read_only_fields = ['id', 'customer', 'created_at']


#item serializers
class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'price', 'seller']
        read_only_fields = ['id', 'seller']

    def create(self, validated_data):
        request = self.context.get('request')
        seller = request.user
        item = Item.objects.create(seller=seller, **validated_data)
        return item
    

#cart serializer
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'item', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items']


#favourie items
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'item', 'created_at']
        read_only_fields = ['user', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'item', 'rating', 'comment', 'created_at']



class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = ['id', 'user', 'subject', 'message', 'created_at', 'resolved']
