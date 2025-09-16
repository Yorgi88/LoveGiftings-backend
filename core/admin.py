from django.contrib import admin
from .models import User, Product, Category, Cart, CartItem, Order, OrderItem, Payment



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "session_id", "total_price", "created_at")
    search_fields = ('session_id',)
    inlines = [OrderItemInline]

admin.site.register(User)
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem)
admin.site.register(Payment)

# # Register your models here.d








# from django.contrib import admin
# from .models import User, Product, Category, Cart, CartItem, Order, OrderItem, Payment


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 0  # Don't show extra empty rows


# class OrderAdmin(admin.ModelAdmin):
#     list_display = ("id", "session_id", "total_price", "created_at")
#     search_fields = ('session_id',)   # Search by session_id
#     list_filter = ('total_price',)    # Filter orders by total price
#     inlines = [OrderItemInline]       # Show related OrderItems in detail view


# admin.site.register(User)
# admin.site.register(Product)
# admin.site.register(Category)
# admin.site.register(CartItem)
# admin.site.register(Cart)
# admin.site.register(Order, OrderAdmin)  # Attach custom admin with inlines
# admin.site.register(Payment)


