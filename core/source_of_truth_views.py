from rest_framework import viewsets, status, generics
from .models import User, Payment, Product, Category, Cart, CartItem, Order, OrderItem
from .serializers import UserSerializer, ProductSerializer, CategorySerializer, CartSerializer, CartItemSerializer, OrderItemSerializer, OrderSerializer, PaymentSerializer
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.conf import settings
import uuid
import hmac
import hashlib
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from decimal import Decimal
import requests
import logging

logger = logging.getLogger(__name__)

# Create your views here.
"""
in this view, we create for now Product view, category view and user view
"""

"""user view"""
# ⚠️ Note: UserViewSet is exposed publicly — restrict access in production
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

"""Category View"""
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

"""Product View"""
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'


    def get_queryset(self):
        queryset = Product.objects.all()
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset
    

class CartViewSet(viewsets.ModelViewSet):
    """see the docs for explanation"""
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(detail=False, methods=['post'], url_path='add')
    def add_to_cart(self, request):
        user = request.user if request.user.is_authenticated else None
        data = request.data
        print("🚨 DATA RECEIVED:", data)

        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        customizations = data.get('customizations', {})
        session_id = data.get('session_id')

        # print(product_id)
        # print(quantity)
        # print(customizations)
        # print(session_id)

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(id=product_id)
            print("✅ Product fetched:", product)
        except Product.DoesNotExist:
            print("❌ Product not found with ID:", product_id)
            return Response({'error': 'Product not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("❌ Error while fetching product:", e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        """Now to get or create cart"""

        if user:
            cart, created = Cart.objects.get_or_create(user=user, checked_out=False)
        elif session_id:
            cart, created = Cart.objects.get_or_create(session_id=session_id, checked_out=False)
        else:
            return Response({"error": "User or SessionID required"}, status=status.HTTP_400_BAD_REQUEST)
        
        """Check if same prod with same customizations exist"""
        existing_item = CartItem.objects.filter(
            cart=cart,
            product=product,
            customizations=customizations
        ).first()  #see the docs for explanations

        
        """ its like sayin if i select a the same cup with same customization, treat as one
        but increase quantity"""
        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            try:
                print("✅ Creating cart item with:")
                # print("  Cart:", cart)
                # print("  Product:", product)
                # print("  Quantity:", quantity)
                # print("  Customizations:", customizations)

                cart_item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    customizations=customizations
                )
                print("✅ Cart item created:", cart_item)
            except Exception as e:
                print("❌ Error saving cart item:", e)
                return Response({"error": str(e)}, status=400)



        subtotal = sum(item.product.price * item.quantity for item in cart.items.all())
        print(f"✅SUBTOTAL {subtotal}")

        return Response({
            'message': 'Item added to cart',
            'cart_subtotal': subtotal,
            'cart_items_count': cart.items.count()
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["GET"], url_path="items")
    def get_cart_items(self, request):
        user = request.user if request.user.is_authenticated else None
        session_id = request.query_params.get('session_id')
        
        if user:
            cart = Cart.objects.filter(user=user, checked_out=False).first()
        elif session_id:
            cart = Cart.objects.filter(session_id=session_id, checked_out=False).first()
        else:
            return Response({"error": "User or Session_id required"}, status=400)
        if not cart:
            return Response({"message": "Cart is empty"}, status=200)
        
        serializer = CartSerializer(cart)  #convert Cart obj into json so
        """in the serializer we see CartSerializer has items which is a list of cartitems to we
        serialize that too"""
        return Response(serializer.data, status=200)
    

    """we want to create the proceed to checkout function here"""
    @action(detail=False, methods=['POST'], url_path='checkout')
    def proceed_to_checkout(self, request):
        user = request.user if request.user.is_authenticated else None
        session_id = request.data.get('session_id')

        if not user and not session_id:
            print('🧧 user or session_id required')
            return Response({'error': 'User or Session_id required'}, status=status.HTTP_400_BAD_REQUEST)
        
        """we move on to exception handling"""
        try:
            cart = None
            if user:
                cart = Cart.objects.filter(user=user, checked_out=False).first()
            elif session_id:
                cart = Cart.objects.filter(session_id=session_id, checked_out=False).first()
            if not cart:
                print('🧧 No active cart found')
                return Response({'error': 'No active cart found'}, status=status.HTTP_404_NOT_FOUND)
            
            cart_items = CartItem.objects.filter(cart=cart)
            if not cart_items.exists():
                print('🧧 cart is empty')
                return Response({'error': 'cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
            """calc total"""
            total_price = sum(item.product.price * item.quantity for item in cart_items)

            """Create Order (inside a transaction block to ensure DB integrity)"""
            with transaction.atomic():
                order = Order.objects.create(
                    user = user if user else None,
                    session_id = session_id if not user else None,
                    total_price = total_price,
                    status='pending'
                )

                """loop through the cart items"""
                for item in cart_items:
                    OrderItem.objects.create(
                        order = order,
                        product = item.product,
                        quantity = item.quantity,
                        customizations = item.customizations,
                        price = item.product.price
                    )
                """mark cart.checked out as true"""
                cart.checked_out = True
                cart.delete()
               
                print("✅ Order created successfully with ID:", order.id)

            return Response({
                'message': 'checkout successful, order created',
                'order_id': str(order.id),
                'total_price': str(order.total_price),
                'status': order.status,
            }, status=status.HTTP_201_CREATED)
        except Product.DoesNotExist:
            print('😂 product does not exists')
            return Response({'error': 'one or more prods not found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




    
    """view to delete cart items from the CartPage.jsx"""

class DeleteCartItemView(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]


class CheckoutSummary(APIView):
    """tis for the checkout page.jsx, where we display the order_id, total_price, etc"""
    def get(self, request):
        session_id = request.query_params.get('session_id')

        if not session_id:
            return Response({"error":"session_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            order = Order.objects.get(session_id=session_id, status="pending")
        except Order.DoesNotExist:
            print("Order in CheckoutSummary not found")
            return Response({"error": "No active order found"}, status=404)

        # ✅ Use OrderItem.price instead of Product.price
        total_price = sum(item.price * item.quantity for item in order.items.all())

        return Response({
            "id": order.id,
            "total_price": total_price,
        })

"""to delete order in the Checkout.jsx page"""
class CancelOrder(generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = "pk"


class InitializePayment(APIView):
    def post(self, request):
        order_id = request.data.get('order_id')
        email = request.data.get('email')
        amount = request.data.get('amount')

        """we then fetch the particular order"""
        order = get_object_or_404(Order, id=order_id)

        """we then need to generate a unique reference"""
        reference = str(uuid.uuid4())

        """we prepare the paystack request"""
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        callback_url = request.build_absolute_uri(reverse("paystack-callback"))
        data = {
            "reference": reference,
            "email": email,
            "amount": int(amount * 100), #convert to kobo
            "callback_url": callback_url
        }

        try:
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                headers=headers,
                data=data,
                timeout=10
            )
            res_data = response.json()
        except requests.exceptions.RequestException as e:
            return Response({
                "status": False,
                "message": f"Network error:  {str(e)}"
            }, status=500)
        
        """only create Payment if paystack flags in as successful"""
        if res_data.get('status') is True:
            Payment.objects.create(
                order = order,
                email = email,
                amount = amount,
                reference = reference,
                status ='pending'
            )
            return Response(res_data, status=200)
        
        """if it fails"""
        return Response(
              {"status": False, "message": res_data.get("message", "Payment init failed")},
              status=400
        )

        """then we save to db"""

    
    
"""After initializing our payment we need to Verify is, if it actually occurred, 
if so we get a reference, that is the uuid if not, then the payment wasn't successful"""
@api_view(['GET'])
def verify_payment(request, reference):
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
    }

    """WE NOW SEND GET REQ TO PAYSTACK"""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
    # for network errors that occur
    except requests.exceptions.RequestException as e:
        return Response({"error": "Network Error", "details": str(e)}, status=500)
    
    """check if paystack request itself was successful"""
    if not result.get('status'):
        print("🧧 Paystack verification failed")
        return Response({
            "error": "Paystack verification failed" ,
            "details": result
        }, status=400)
    
    """paystack returned data"""
    data = result['data']

    try:
        """lets look at our own database for this payment"""
        payment = Payment.objects.get(reference=reference)

    except Payment.DoesNotExist:
        print("🧧Payment not found in db")
        return Response({"error": "Payment not found in our system"}, status=404)
    

    """update our db record with paystack results"""
    payment.status = data.get("status", payment.status)
    paid_at = data.get("paid_at")
    if paid_at:
        payment.paid_at = paid_at
    # payment.paid_at = data.get("paid_at", payment.paid_at)
    amount_kobo = data.get('amount')
    if amount_kobo:
        payment.amount = amount_kobo / 100
    # payment.amount = data.get("amount", payment.amount) / 100  #conv back to naira
    payment.save()

    print("✅ Payment verified successfully")
    return Response({
        "message": "payment verified successfully",
        "status": payment.status,
        "amount": payment.amount,
        "email": payment.email,
        "reference": payment.reference,
    })


# we need to create a WEbhook and callback view next
@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")

    """verify the webhook came from paystack recreate the signature and compare"""
    expected_signature = hmac.new(
        key = settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        msg = payload,
        digestmod = hashlib.sha512
    ).hexdigest()

    if signature != expected_signature:
        print("🛑 Invalid Paystack signature")
        return HttpResponse(status=400)
    
    try:
        event = json.loads(payload) #turn it into a py dict
    except json.JSONDecodeError:
        print("🛑 Invalid JSON in webhook")
        return HttpResponse(status=400)

    event_type = event.get('event')
    data = event.get('data', {})

    reference = data.get('reference')
    if not reference:
        print("🛑 No reference in webhook payload")
        return HttpResponse(status=400)
    
    try:
        """we find the reference in our database"""
        payment = Payment.objects.get(reference=reference)

    except Payment.DoesNotExist:
        print(f"🛑 Payment with reference {reference} not found")
        return HttpResponse(status=400)
    
    if event_type == "charge.success":
        # we double check amount
        if int(data.get("amount", 0)) == int(payment.amount * 100):
            payment.status = "success"
            payment.paid_at = data.get("paid_at")
            payment.save()
            print(f"✅ Payment success recorded for {reference}")
        else:
            print("🛑 Amount mismatch in webhook")

    elif event_type == "charge.failed":
        payment.status = "failed"
        payment.save()
        print(f"❌ Payment failed for {reference}")

    return HttpResponse(status=200)


def paystack_callback(request):
    """callback view that paystack redirects the users to after payment"""

    # get the reference
    reference = request.GET.get('reference')
    if not reference:
        print("🧧Error occurred in paystack callback")
        return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed/unknown")
    
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"❌ Paystack verification request failed: {e}")
        return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed/{reference}")
       

    result = response.json()


    """we double check payment status"""
    if result.get('status') and result['data']['status'] == 'success':
        print("✅ Payment successful")

        try:
            payment = Payment.objects.get(reference=reference)

            """we double check and verify if the amount matches"""
            if int(payment.amount * 100) != result['data']['amount']:
                logger.warning("⚠️ Payment amount mismatch in Paystack callback")
                return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed/{reference}")


            payment.status = 'success'
            payment.paid_at = result['data'].get('paid_at')
            payment.save()
            return redirect(f"{settings.FRONTEND_BASE_URL}/payment/success/{reference}")
        except Payment.DoesNotExist:
            print("🧧 Payment Does not exist at Paystack callback func")
        return redirect(f"/payment-details/{reference}?status=success")

    else:
        logger.warning(f"⚠️ Payment failed for reference {reference}")
        
        try:
            payment = Payment.objects.get(reference=reference)
            payment.status = "failed"
            payment.save()
        except Payment.DoesNotExist:
            logger.error(f"❌ Failed payment with reference {reference} not found in DB")
            return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed/{reference}")

        return redirect(f"/payment-details/{reference}?status=failed")




    
    
    
"""views for counting the number of guests who interacted with the application, as per guests who checked out"""

"""view for summation of payments accrued so far."""

