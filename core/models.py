from django.db import models
import uuid
# Create your models here

class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=250, unique=True)
    password = models.CharField(max_length=100)
    # do we need id
    # also, do we use the session id now or later
    def __str__(self):
        return f"{self.name}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name='subcategories', null=True,
                               blank=True) #i need to understand this part
    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    # the category part means a product belongs to one category, but a category can house various prods
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    # in this, we need img, prod-name, description, price, slug too 
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    img = models.ImageField(upload_to='products/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
"""Don't forget the forms the users have to fill, i think it will be in the cart or cartitem model """
# class Order(models.Model):
#     """
#     in this, when the user cli
#     """

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    # i think many carts can belong to one user, a user can have many products in their carts
    session_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # what about total-price or subtotal?
    # also remove cart feature, perhaps we only need to send a del req
    checked_out = models.BooleanField(default=False) 

class CartItem(models.Model):
    """This means each product stored in the cart is a cartitem
    its linked to Cart, Product models, it includes quantity and the customizations(jsonField)"""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    customizations = models.JSONField(default=dict)


"""
✅ Overview of the Checkout Flow
User reviews items in CartPage

Clicks "Proceed to Checkout"

You create an Order instance

You move each CartItem into OrderItem

Set the Order status to "Pending"

Generate an Order ID (can be UUID or auto-incremented)

delete/clear the cart after successful order creation"""



class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    # find out what this SETNULL and blank and all that is
    session_id = models.CharField(max_length=255, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # status = None we need only three states, pending, delivered, cancelled
    # also the dev or admin should do this manually, like ticking a checkbox or so
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    customizations = models.JSONField(default=dict)  # e.g. {"color": "red", "engraving": "Love"}
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at the time of purchase



class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    reference = models.CharField(max_length=120 ,unique=True)
    status = models.CharField(max_length=30, default='pending')
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.amount} - {self.status}"


    