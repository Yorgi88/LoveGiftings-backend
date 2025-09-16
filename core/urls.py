from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, CategoryViewSet, ProductViewSet, CartViewSet, DeleteCartItemView, InitializePayment, verify_payment, paystack_webhook, paystack_callback, CheckoutSummary, CancelOrder, GetUserOrder

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"products", ProductViewSet)
router.register(r"categories", CategoryViewSet)
router.register(r"cart", CartViewSet, basename='cart')




urlpatterns = [
    path('api/', include(router.urls)),
    path('api/cart/items/delete/<int:pk>/', DeleteCartItemView.as_view(), name='delete_item'),
    path('api/checkout/summary/', CheckoutSummary.as_view(), name='checkout-summary'),
    path('api/order/delete/<uuid:pk>/', CancelOrder.as_view(), name='delete-order'),
    path('api/orders/', GetUserOrder.as_view(), name='user-orders'),
    # for the payment urls

    path('api/paystack/initialize/', InitializePayment.as_view(), name='initialize-payment'),
    path('api/paystack/verify/<str:reference>/', verify_payment, name='verify-payment'),
    path('api/paystack/webhook/', paystack_webhook, name='paystack-webhook'),
    path('api/paystack/callback/', paystack_callback, name='paystack-callback'),  
]




