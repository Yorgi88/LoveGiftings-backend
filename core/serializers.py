from rest_framework import serializers
from .models import User, Product, Cart, CartItem, Order, OrderItem, Category, Payment
import os
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    static_image = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = "__all__"
    
    def get_static_image(self, obj):
        filename = None
        candidates = ("img", "image")
        for attr in candidates:
            val = getattr(obj, attr, None)
            if not val:
                continue
            if hasattr(val, 'name') and val.name:
                filename = os.path.basename(val.name)
                break
            if isinstance(val, str) and val.strip():
                filename = os.path.basename(val)
                break
        if not filename:
            print("🧧 Filename not found")
            return None
        request = self.context.get('request') if hasattr(self, 'context') else None
        static_path = f"/static/products/{filename}"

        if request:
            return request.build_absolute_uri(static_path)
        
        base = getattr(settings, 'BACKEND_BASE_URL', '').rstrip('/')
        if base:
            return f"{base}{static_path}"
        return static_path


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'customizations', 'price']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(read_only=True, many=True)
    class Meta:
        model = Order
        fields = "__all__"

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'customizations']
    


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    """like the items in the cart, since an item is == a product, i think, lol"""
    subtotal = serializers.SerializerMethodField()
    checked_out = serializers.BooleanField(read_only=True) 
    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'created_at', 'items', 'subtotal', 'checked_out']

    def get_subtotal(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

    

class PaymentSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"

# will there need be any changes as per customizations on the serializer

