So in the Models.py, we don't need to create the session_id in the User model
it will be in the Carts/Order model

    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name='subcategories', null=True,
                               blank=True) #i need to understand this part

<!-- 🔍 What does it mean?
It’s saying:

“A Category can belong to another Category — i.e., be a subcategory of a parent category.”

This is called a self-referential foreign key — a model pointing to itself.

🧠 Simple Example
Imagine you have categories:

Bottles (Main category)

Stylish Bottles (Subcategory)

Temperature Bottles (Subcategory)

Now, Stylish Bottles and Temperature Bottles will have:

python
Copy
Edit
parent = Bottles
So Bottles is the parent, and the other two are children (or subcategories).

🧱 null=True, blank=True
This just means:

The category can be a top-level one (not have a parent).

So top-level ones like Journals, Giftpacks, etc. will have parent = null.
 -->




 --------------> PAYMENT MODEL
class Payment(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)  # e.g., "Paystack"
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed')
    ])
    transaction_ref = models.CharField(max_length=255)
    paid_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.status}"




 ✅ So… where does self.order.id come from?
Let’s unpack it slowly:
🧱 Your Payment model looks like this:
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    ...
This means:

Each Payment is linked to one specific Order

That order is stored in the order field of the Payment model

Django lets you access the related order object using self.order

🔑 And then .id?
Every Django model has an id field by default (unless you change it).

In your case:

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
So instead of Django's default integer id, you’re using a UUID (e.g., 8e2b4d38-8a12-4db1-9b9e-51c9e4a5afc2).

That id is unique and identifies the order.

✅ What the line does:
return f"Payment for Order {self.order.id} - {self.status}"
It’s saying:

“When Django wants to display this payment in the admin or shell, show a string like:
Payment for Order 8e2b4d38... - Success”




--=---------------
NEXT WE MOVE ON TO THE SERIALIZERS, we need to serialize our models

in the core dir, create a serializer.py file.

So i pasted the code which i came up with: and then gave ai for review,
ai corrected the order and order item, also the cart and cart item serializers

in the Cart Serializer we also added a subtotal field:
class CartSerializer(serializers.ModelSerializer):
    items = ProductSerializer(many=True, read_only=True)
    """like the items in the cart, since an item is == a product, i think, lol"""
    subtotal = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ['id', 'user', 'session_id', 'created_at', 'items', 'subtotal']
we don't need to save subtotal to the database, we just calc it dynamically and display on frontend

we can add this to the views:
    def get_subtotal(self, cart):
        return sum(
            item.product.price * item.quantity
            for item in cart.items.all()
        )
for future or later reference


----> Note that we'll resume the Payment model and serializer later


--------------->>>>>>>>>>>>>>>.

we've built the views so check it out, we only built three for now

next is the routers in urls

NEXT we create a folder in the love-giftings dir called media, i think its for the images
Now in the settings.py remember we did some MEDIA stuff, where we will store the imgs of product and whatnot
we also made some changes in the templates section in the settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'frontend', 'build')],  <<<---HERE>>>
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

next we go to the admin.py, create super user and all that
first->> makemigrations and migrate, then create super user




--->>>> I think we move to the frontend now, where we use redux and all that, phew!

Since we using RTK , we set upp a dir called app in the src dir

also we create a features dir, and in the dir, we create 2 dirs product and cart

in the product dir, create a file productSlice.js

next we do that Provider thingy that we normally do in the main.jsx
where we import store

import {store} from './app/store.js';




createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Provider store={store}>
         <App />
    </Provider>
   
   
  </StrictMode>,

  next go to the productSlice.js and fetch the api and all that


  createSlice: lets us create a "slice" of the Redux state (here, the product state)

createAsyncThunk: helps us write async logic (like calling an API)

axios: used to make HTTP requests


🧱 Step 2: Define the Initial State
const initialState = {
  products: [],
  isLoading: false,
  error: null,
}


This is the starting state of our products slice:

products: the list of products we get from the backend

isLoading: shows a spinner while products are loading

error: stores any error message if fetching fails



🚀 Step 3: Create the Async Thunk (API Call)
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";

const initialState = {
    products: [],
    isLoading:false,
    error:null,
}


export const fetchProducts = createAsyncThunk (
    'products/fetchProducts',
    async (categorySlug='', thunkAPI) => {
        try {
            const resp  = await axios.get (
                categorySlug ? `/api/products/?category=${categorySlug}` : '/api/products'
            )
            return resp.data;
        } catch (error) {
            return thunkAPI.rejectWithValue(error.response.data)
        }
    }

)

const productSlice = createSlice({
    name:'products',
    initialState,
    reducers: {},
    extraReducers: (builder)=>{
        builder
            .addCase(fetchProducts.pending, (state)=>{
                state.isLoading = true;
                state.error = null
            })
            .addCase(fetchProducts.fulfilled, (state,action)=>{
                state.isLoading = false;
                state.products = action.payload;
            })
            .addCase(fetchProducts.rejected, (state,action)=>{
                state.isLoading = false;
                state.error = action.payload;
            })
    }
})
export default productSlice.reducer;







🔍 What’s going on here?
createAsyncThunk is like useEffect + useState + fetch but for Redux.

We're defining a new action called 'products/fetchProducts'.

When this action is dispatched, it makes a GET request to /api/products/.

💡 If a categorySlug is passed (e.g., bottles), it adds ?category=bottles to filter products from Django backend.

If it works:

The data is returned and used inside our reducer.

If it fails:

We return the error with rejectWithValue, which will go into our error state.



Here’s what’s happening:

name: 'products'
That’s just a label. Redux Toolkit uses it under the hood.

initialState
Connects the slice to the initial data we defined above.

reducers: {}
Right now, we don't have any non-async reducers (like addToCart, etc.) — just async ones.

extraReducers
This is where we handle the async flow:

Action	What it does
fetchProducts.pending	Triggered when request starts — shows a loader
fetchProducts.fulfilled	Triggered when data is fetched — saves products to state
fetchProducts.rejected	Triggered if there's an error — saves the error





class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name='subcategories', null=True,
                               blank=True) #i need to understand this part
    def __str__(self):
        return f"{self.name}"

first of, when we getting products by category, is the the name er get or the slug?
ask ai


----->>>>> I have fetched it successfully from the backend, i encountered two errors
FIRST: products.map(())...not a function, so just add http://localhost:8000 to your api reqs

SECOND, was violating CORS policy so just don't forget to add corsMiddleware and all that in the 
middleware section in the settings.py




----------->>>>> NEXT I WANT TO BUILD THE NAVIGATION using react-router-dom
this is a snippet from the tutorial code course i took, take a look:
   <Link to={`/products/${product.slug}`} className='btn btn-primary'>View Details</Link>
IN MY OWN CASE, since at the very homepage we are fetching the products by category and displaying them in each sections

when the user clicks VIEW DETAILS or the particular product img
we take the user to the product details showing that particular prod, img, desc, etc
so in the Link component i think ours will be `/products/category/${product.slug}`
const product = products.find(p => p.slug === slug);


--->>>>>>  THINKING
I don't know how delivery fee is calc so i have to read on that worst case, it will be without delivery fee

Also, as per forms aspect: all the Journal, cUps, bottles will basically have the same form fields
except Gift_packs

Color -->
Inscription -> 
Phone No -> //we want to reach out to you placeholder

Address or Should we say Location, it will be a selected form showing
Abk, Ogun State
Sagamu, Ogun State
Ijebu-Ode, Ogun State
Ijebu-igbo. Ogun State
Ibadan, Oyo State
Ikeja, Lagos State
Lekki, Lagos State
Other

An Add to Cart/Orders Button below




For Giftpacks I am thinking of using a different Product details page
will be called ProductDetailsGift page
so when a user clicks on a gift prod, the user gets taken to this page

same ui but different form fields

FORM FIELDS
Should we add Color ->
Recipient -> Male / Female options
Location -> same as above
What else would you like to add? perhaps for the user to add an item or two
that he or she would like to be included in the Gift. should it be added or not?

then Below add to cart button


----->>>>>>>>
I ADDED SOME PRODUCTS in the admin.py journals, cups, bottles

so i fetched it on the frontend, 
apart from the BrowserRouter error i am seeing on the console

i gt this component errors, like only the Journal component is showing and not the Bottle comp

they should be in sections,
also when i reload the page, the position of the comp changes
like if Bottle comp was at the top and journal at the bottom, it will switch position when you reload
why???????????\

--✅ Twas a state conflict, its like the products i'm fetching are cancelling eachother or overwriting eachother
we fixed the bug by making some changes in our productSlice file
we need to send the specific reqs on what we need either journals, cups etc so we send a req along 
with an arg eg 'bottles' to the backend
that way they won't overwrite eachother

🛠️ What did we do to fix it?
We changed the structure of the Redux state to store data category by category.

Instead of:
products: []

We did this:
productsByCategory: {
  bottles: [...],
  journals: [...],
  and the rest
}

We made sure that each API response comes with its category:
return { category: categorySlug, data: response.data }


This way, Redux knows which category the data belongs to.

state.productsByCategory[category] = data;
so when we make a request to only fetch bottle
look at the productsByCategory
iw will be like this bottles = productByCategory['bottles] || [];
the same for the rest of them



Update, now i have fetched all products and done the routing, up to the product details

lets explain what happened in the product details

remember that useEffect runs code when components load
useParam gets the slug from the url
dispatch for callin redux actions eg fetchProducts

const productsByCategory = useSelector((state) => state.products.productsByCategory);

remember in our productSlice file, productByCategory is an obj

{
    journals: [journal1, journal2...],
    bottles: ['bottle1, bottle2 ...]
}
the way i understand it , our store.js has products: productSlice or reducer i think

so state.products as in the highlevel of things, then we go down further since we want to get the specific prod category and the specific prod

state.products.productsByCategory




Now back to the useEffect, -> on the first load or refresh, the redux store might be empty
and if empty fetch app prods, using the dispatch


then, merge all into arrays as per values

Now its an array form, then you can use the p.find() logic now

phew!



NEXT IS THE UI FOR THE PRODUCT DETAILS , FORM AND ADD TO CART FEATURE

recall that handlechange updates the form when the user types
for example: color: red
the color is the name, red is value

handleSubmit sends the form to the backend or logs the form

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };
e.target refers to the form elem the user just interacted with
2. const { name, value } = e.target;:
This extracts:

name — the name of the field (e.g., "color" or "phone")

value — the current value typed/selected by the user



3. setFormData((prev) => ({ ... })):
This updates your formData state. It uses the previous state (prev) and creates a new updated version of it.

...prev:
This copies all existing fields in the form, like:
{
  color: "red",
  inscription: "Happy Birthday",
  phone: "08012345678",
  location: "Ibadan"
}
[name]: value:
This uses the field's name to dynamically update the correct key.

So if name = "color" and value = "blue", you get:
{
  ...prev,
  color: "blue"
}

🧧❤🧧  WE CANCELLED THIS METHOD, AND MADE USE OF useRef in react -->

The way i understand this, useRef is a react hook, that saves up whatever data and then gives it back to you when you need it

it is like sayin 'hey, look at this formdata, help me save it and when i call you, give it here'


see the Forms.jsx and FormGift.jsx

in the prod details page we pass in customizationRef as prop to the forms

const customizationRef = useRef();

          {product.category.slug === "giftpacks" ? (
            <FormGift product={product} ref={customizationRef} />
          ) : (
            <Form ref={customizationRef}/>
          )}

then you receive the prop in the Forms or FormGift 

there is a way you do this when  it comes to useRefs 
you need to import forwardRef and useImperative something, see Forms and Forms.jsx


to see how its done:




------------->>>>>> EXPLAINING CART FEATURE

When a user clicks "Add to Cart" on a product (like a journal, bottle, or cup), we want to save that product somewhere, so when the user later opens the cart page, they can see everything they picked before checkout.

We’re building this in Django (the backend), and the frontend (like React) will send a request to the backend when the "Add to Cart" button is clicked.

👩‍💻 First, Understand the Players:
Here’s what’s involved:

🛒 The Cart
This is like the shopping basket. It belongs to:

a logged-in user OR

a guest user, using something like a session_id to identify them.

🧾 The CartItem
Every product the user adds (like “Red Journal, Qty: 2”) becomes a CartItem.

It stores:

The product (e.g., Journal)

Quantity (e.g., 2)

Customizations (e.g., "color": "red", "inscription": "For Mom")


 What Happens When You Click “Add to Cart”?
Let’s break it down:

1. Frontend Sends a Request
When the user clicks “Add to Cart,” your frontend sends a POST request to the backend with this info:

{
  "product_id": 3,
  "quantity": 2,
  "customizations": {
    "color": "red",
    "inscription": "Love You"
  },
  "session_id": "abc123"
}
This is like saying: “Hey server, I want to buy 2 of product #3 with these customizations.”

2. Backend Gets or Creates a Cart
On the backend, we check:

If the user is logged in, we use their account (request.user)

If not, we check for a session_id

If the user doesn’t have a cart yet, we create one for them.

3. Check for matching item

its like saying if a user add the same prod with the same customizations to the cart, we don't, we don not treat this as 2, instead we only increase its quantity 

if the user add the same prod with diff customizations, we treat as separate


✔✔🧧✅ lOOK AT THE CARTSLICE FILE  in the addToCart func, we need to ensure consistency through out our post reqs
we need to create a session_id, normally i thought, with the django backend that we wrote, the session id will 
be created for us, but i don't think that's the case, so we create an utils dir on the frontend (src)

then we create a session.js file =>  see session.js:

so we export tis function to the cartSlice file and include it in our req to the backend
so that way our backend can store these reqs, i think it the CartItems model


also, look at the decorator in the add_to_cart view, the url path is "add"
so the cart slice will be like => see cartSlice.js






4. We calc the subtotal
subtotal = sum(item.product.price * item.quantity for item in cart.items.all())


After this the backend sends a resp like this:
{
  "message": "Item added to cart",
  "cart_subtotal": 4000,
  "cart_items_count": 3
}


Part	Meaning
@action(detail=False, methods=['post'], url_path='add')	
Defines a custom POST route like /api/cart/add/ to handle special logic like adding to cart.

        existing_item = Cart.objects.filter(
            cart=cart,
            product=product,
            customizations=customizations
        ).first()

✅ What’s going on here?
You're checking:
“Is there already a CartItem in this cart that:

belongs to the same cart (cart=cart)

has the same product (product=product)

and the same customizations (like color, text, etc)?”

If yes, it will return it.
If no, it returns None.



------->>>>>>>> 😗FETCH CART ITEMS(items stored in the cart)
remember above we have written how the cart is stored, so now
we want to fetch the cart-items

so we write our getCartItems view on the backend --> see views.py

so we define a custom GET route usin the decorator, and the url_path will be "items"

so in the cartSlice, the fetchCart func, you will adjust the url path

/api/cart/items/

also we include session_id in our get req, --> see cartSlice.js
since users aren't like;y authenticated yet, so they will be operating the web app based on session_id

till we authenticate the session id users and make them actual users




Now, 😘👌 --> in the CARTPAGE>JSX 
we ran into errors saying 'items.map(()) is not a function'

remember out in our cartSlice file, in the initial state, items = [] array

but you see actually, our items fetched from the backend is an obj {} and that obj

contains our items array, like this:  {
    itemID
    quantity
    items: [] contains, product details too, etc
}

so to actually access this we need to say state.cart.items
remember the 'cart' was designated in out store.js in the frontend

so in the cartpage .jsx fix the code accordingly, --->>>>> see CartPage.jsx

we also use an approach to calculate the totalPrice on the frontend using reduce()

know that our backend also calc the subtotal too

note that to access the product details like name , price, image
we do this -> item.product.price or name or img and so on

we will work on the REMOVE BUTTON, I THINK 
it should remove based on item.id not item.product.id
we will to the deleteCart func in the cartSlice









   --------------------REQUIREMENTS ------------------>>>>>>>

   BACKEND:

asgiref             3.8.1  
Django              4.2.23 
django-cors-headers 4.7.0  
djangorestframework 3.16.0 
pillow              11.2.1 
pip                 25.1.1 
setuptools          58.1.0 
sqlparse            0.5.3  
typing_extensions   4.14.0
tzdata              2025.2
django env or so



FRONTEND:

├── @eslint/js@9.20.0
├── @reduxjs/toolkit@2.8.2
├── @types/react-dom@19.0.3
├── @types/react@19.0.8
├── @vitejs/plugin-react@4.3.4
├── axios@1.10.0
├── bootstrap-icons@1.11.3
├── bootstrap@5.3.3
├── eslint-plugin-react-hooks@5.1.0
├── eslint-plugin-react-refresh@0.4.18
├── eslint-plugin-react@7.37.4
├── eslint@9.20.0
├── globals@15.14.0
├── react-bootstrap@2.10.9
├── react-dom@19.0.0
├── react-multi-carousel@2.8.6
├── react-redux@9.2.0
├── react-router-dom@7.6.3
├── react-slick@0.30.3
├── react@19.0.0
├── slick-carousel@1.8.1
├── sweetalert2@11.22.1
└── vite@6.1.0



-------------------------------------

NOW WE HAVE WRITTEN THE CART LOGIC, LETS MOVE TO THE FRONTEND SIDE OF THINGS

for the forms GPT suggested , useRef, if i remember correctly see above for more exp on use?Ref

useRef is a way of telling a friend who helped you keep notes, that you need the notes back

so in the form the useRef helps to save the state i think, then wen we need it , it gives us back

Think of useRef like a direct line or wire to a specific component or element. It allows you to talk to a child component (like a form) and ask it to give you something — like the data it holds — without causing re-renders.



----------------------------------------------------------------------


NEW we have fixed all of it our cart now works 

the little problems are:

2. remove btn and functionality
3. Proceed to checkout feature --> here is when we implement auth

i guess we should tackle this remove first, we will probably need to create views for it in the backend

After, lets look at the Cart count, we have made an icon to display the cart items amount

so i think we get the count in the cart page pf the items in then probably use useContext and receive it in the navbar section where we'll con

 📍📍 Checck out this minor error that happens when you add to cart:  

 cartSlice.js:78 Uncaught (in promise) TypeError: state.items.push is not a function
    at cartSlice.js:78:25



👋👋 Note that our structure is like this:

state.cart.items {
  items: [... ...  .....]
}
so to access the items in the obj we say state.cart.items.items

see the CartPage.jsx and see the cartSlice in the removeCart reducer

according to ai it could cause confusion and tech debts in future so my idea is to
flatten the array as per the api structure 

question is how do i do that and where? CartPage? cartSlice?



---------------------->>>>> REMOVE BTN FUNCTION
For the remove, we initially wanted to use stuffs from the cartSlice => cartSlice.js

but we ran into some issues with the builder.addcade({

})
so we thought of something else, sending the delete req right from the CartPage.jsx
so we imported axios and all and passed in an id as params => see CartPage.jsx

  const handleRemove = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/api/cart/items/delete/${id}/`);
      dispatch(fetchCartItems());
    } catch (error) {
      console.error("An error occurred", error);
    }
  };

since we couldn't use the deleteCartItem reducer in the cartSlice due to the complications of the project
for example,  useSelector((state)=> state.cart.items.items) lol complicated right?  i think it from the structure of our backend api and whatnot, its an object {} type
{
  items: []
}
lets just hope we won't rack up technical debt

because of this wwe can't delete items from the cart in a smooth manner

so we go to the other route, for every cart item we delete, we re-fetch the cartitems( dispatch(fetchCartItems());) all over again, not the best case, but we're trying to build and ship fast, we worry about performance and best practices later so help us God.

this way the remove feature works, also on the backend we created views for it => see views.py

class DeleteCartItemView(generics.DestroyAPIView):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [AllowAny]
then we configure thr urls => see urls.py and make sure we are making the right call from the frontend to the backend to delete


-------------------------------------------
Cart Item Count FEATURE

------------------------

So next, we want to build the cart item count feature were users can see see the amount of cart items the've added to their respective cart this feature is normally added in the NavBar section -> see NavBar.jsx

we use the quantity to get the count;

   const cartItems = useSelector((state)=>state.cart.items.items) || [];
   const itemCount = cartItems.reduce((total, item)=> total + item.quantity, 0);
we count based on item.quantity and return it in form  of.... 

        <Nav.Link href="#cart" className="fw-bold text-dark ms-auto" as={Link} to={'/cart'}>
            <i className="bi bi-cart"></i> Cart ({itemCount})
        </Nav.Link>

But there was an issue:

but i have this problem, when you load the app and run it, initially the count is zero, but when you click on the Cart on the frontend, that zero then changes into the actual amount of cart in for example from zero to three, then again, if you refresh the app, it goes back to zero, then again if you go to the cart section it returns the amount count of the cart, why is this so and how do i make it consistent all through?

This is called hydration issue, the cart items are empty initially, only when we click on cart does it fetch cart items from the backend, that why is this way

to make it consistent, we go to the app.jsx and make the fetchCartItems call so when the app loads, it immediately fetches cart items in this case, the cart count is consistent all through

  useEffect(()=>{
    dispatch(fetchCartItems());
  }, [dispatch])

see app.jsx


---------------->>>>> NEXT
I think we can move on to auth

create a dir in src called auth
inside it will have
Auth.jsx
Login.jsx
Register.jsx

i am thinking we should just allow the user to use their emails to register / login
or is there really need for password? find out!

Also we want the UI to be something like this -> Login, Don't have an account? Register
------------------------------------------------

so in the cart page, when the user clicks on proceed to checkout we check if the user is already authenticated

if not? redirect the user to the Auth.jsx page i am thinking the Auth.jsx will house both the register and login.jsx


also for the views we write a logic to convert session_id into auth_id for guest users
research more about that too.



✅ show password feature in the password field

---------------------------------
WE DECIDED TO NOT ADD ANY AUTH FEATURE, JUST A GUEST MODE FEATURE 😂😂 because of the structure, there was an oversight in the user model, and to rectify? We have to start all over this time with the correct user model

So how its gonna go from now

- When a user clicks on proceed to checkout, we don't check if user is auth anymore, else, we just direct the user to the checkout page

--> What would be displayed in the checkout page, the order id, perhaps the total amount to be paid too

and option to pay with transfer or pay with card

- once the user pays, cart will be cleared 
- the user will then be directed to the order info page showing
order id, amount paid and status.


--------------------->> We create a method called proceed to checkout

we created a custom route of course using the @action decorator, with a url path of 'checkout'

----> see proceed_to_checkout in views.py

@action(...) is a Django-REST-Framework shortcut. It creates a custom API route on your CartViewSet.

detail=False → this route does not need a single object ID (it’s for the collection).

methods=['POST'] → this route accepts POST requests (we’re sending data).

url_path='checkout' → the URL will be /api/cart/checkout/ (roughly).

--------------------------

user = request.user if request.user.is_authenticated else None
session_id = request.data.get('session_id')

request.user is set by Django if someone is logged in. If they’re logged in we use that user, otherwise user is None.

session_id is read from the POST body (request.data) — for guest users you track them by a session id stored in the browser.


if not user and not session_id:
    return Response({'error': 'User or Session_id required'}, status=400)

If neither user nor session_id exists, we stop and return an error (HTTP 400 = bad request).

Basically: we need someone to attach the cart to.



if user:
    cart = Cart.objects.filter(user=user, checked_out=False).first()
elif session_id:
    cart = Cart.objects.filter(session_id=session_id, checked_out=False).first()
if not cart:
    return Response({'error': 'No active cart found'}, status=404)



-> We look for the user’s active cart (one that hasn’t been checked out).

.filter(...).first() returns the first matching cart or None if none exists.

If there’s no active cart, return 404 (not found).

since we using guest mode, its only session_id that we'll use to filter out the cart to get the cart of that 
specific guest user


-> cart_items = CartItem.objects.filter(cart=cart)
if not cart_items.exists():
    return Response({'error': 'cart is empty'}, status=400)

-> we get all the CartItems and filter according to the cart variable, remember that the cart var stores the filtered cart of the user that contains the cart items of the user


total_price = sum(item.product.price * item.quantity for item in cart_items)

we calculate the total price of the cart



-> Create the Order and OrderItems inside a DB transaction

with transaction.atomic():
    order = Order.objects.create(user=..., session_id=..., total_price=..., status='pending')
    for item in cart_items:
        OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, customizations=item.customizations, price=item.product.price)
    cart.checked_out = True
    cart.save()


transaction.atomic() means: do everything inside this block as a single unit. If any line fails, the database will undo everything in the block (no partial orders).

Order.objects.create(...) – creates an Order row with total_price and status='pending'.

Loop: for every cart item we create an OrderItem. We copy the product, quantity, customizations, and the product price at this moment so the order keeps the correct price even if the product price changes later.

Finally we mark the cart checked_out = True so it won’t be used again.



-> Print success and return a JSON response


print("✅ Order created successfully with ID:", order.id)

return Response({
    'message': 'checkout successful, order created',
    'order_id': str(order.id),
    'total_price': str(order.total_price),
    'status': order.status,
}, status=201)


------------------>> Next you move to the frontend and call it, go to the CartSlice.js

export const checkoutCart = createAsyncThunk(
    'cart/checkout',
    async(_, {rejectWithValue}) => {
        const session_id = getSessionId();

        try {
            const resp = await axios.post('http://localhost:8000/api/cart/checkout/', {
                session_id,
            });
            return resp.data;
        } catch (error) {
            return rejectWithValue(error.response?.data || 'checkout failed')
        }
    }

);

so we send session_id only as per the guest user

the in the CartPage.jsx, we say:

  const handleCheckout = () => {
    dispatch(checkoutCart())
    .unwrap()
    .then(()=> {
      navigate('/checkout')
    })
    .catch((err)=> {
      console.error('checkout failed', err)
    })

  }


  --- add an onclick event ->        <Button variant="dark" className="w-100 mt-3" onClick{handleCheckout}>
                                                     Proceed to Checkout
                                      </Button>

------------------------------------------------------------------------------

The procedure for the payment integration, we have created a paystack account, and we have got our public and secret key

we also created a .env where we stored these keys, in the settings.py dir

✅🧧

we need to install python dotenv, for us to be able to call these keys

so we say: from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

"""paystack test keys"""
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY') ====>>>>>>>>>>>>>> CONTINUE ON LINE 1112



2️⃣ How the Full Flow Works
User clicks "Pay Now" in React.

React → sends request to Django /api/paystack/initiate-payment/.

Django → talks to Paystack API → gets authorization_url.

Django → sends that URL back to React.

React → redirects browser to Paystack’s hosted checkout.

User completes payment → Paystack:

Redirects user to your callback URL.

Separately sends a webhook event to your /api/paystack/webhook/ endpoint.

Django processes webhook → verifies payment → updates database → notifies frontend if needed.


------------------
EXPLAINING --> 

According to Paystack, we need to include email in a request, so we need to find a way to get the user email and include it in the request

So we need to create a checkout page, and there we will create email field in the frontend and send it to the backend => the backend stores the email in the email field in the payments model

The backend also interacts with the Paystack api to check whether the payment is successful and whatnot

and updates the database accordingly, at the frontend we will also need a callback url -> that is some pages to reflect the payment succeeded or failed from the frontend, so i think we should create two files, one

PaymentSuccess and PaymentFailed jsx
-------------------------------------------------------------------

--> So we also need to install ngrok because the paystadk api can't interact on local development, that is http

we need a medium(https) to fully test the api, so we install ngrok and cd into it in the backend

here its in the Downloads, so we cd into it, and we cd into the name of the folder housing the ngrok app itself

then we say

`ngrok http 8000` command to start the server an https://localhost:8000 or so

--->DEACTIVATE COMMAND IS --> `  `

we then build our checkout page cause we need to send order_id, the total amount, to the frontend
we also need the users email, paystack requires it, so we put an emails field in the frontend
SEE checkout.jsx


on the backend we create a payment mmodel, --> SEE models.py

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=120 ,unique=True)
    status = models.CharField(max_length=30, default='pending')
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

we then need to create 3 views, first view is to Initialize payment, second is to verify payment, third is a webhook/callback view to like send a response for example to the frontend saying,'payment succeeded'

For the first view we need to: 

Accepts the order_id, email, and amount from the frontend.

Generates a unique reference (string) for the payment.

Saves the record in the Payment model with status="pending".

Calls Paystack’s initialize transaction API with the reference + email + amount.

Returns the Paystack authorization URL to the frontend.

🟢 Why Verify Payment?

When a user pays with Paystack, Paystack will send us back a reference (the unique ID we created earlier).

That reference is what we use to check if the payment was really successful.

We don’t trust the frontend saying "oh the user paid" because anyone could fake that.

Instead, we ask Paystack directly: “Hey, for this reference, is the payment really successful?”




🔹 Why do we need both Webhook & Callback views?
-------------------------------------------------

Think of them as Plan A vs Plan B:

1. Callback View

Triggered immediately after the user finishes Paystack checkout.

Paystack redirects the user’s browser → your callback URL (frontend or backend).

Used for instant feedback to the user (“Payment Successful” page).

Problem: if the user closes the browser, has bad network, or Paystack fails to redirect, you lose the payment update.

2. Webhook View

Paystack server → your backend server (direct server-to-server call).

Doesn’t depend on the user’s browser at all.

Always fires for every payment attempt.

Used as the source of truth to update your DB.

✅ So:

Callback = smooth user experience.

Webhook = guaranteed reliability.

Together → rock-solid payments flow.


-------------------------------------------------------
        FLOw
------        -------------------


🔹 1. After the user pays on Paystack

Paystack itself will redirect the user back to the callback_url you gave when initializing payment.
Example: https://yourfrontend.com/payment-details/:reference


That URL is not Paystack’s — it’s your frontend route (yes, PaymentDetails.jsx).

At this point, you don’t yet know if the payment was successful or not.

Paystack only gave you the reference.


🔹 2. What happens inside PaymentDetails.jsx

When your React page loads (/payment-details/:reference):

Grab the reference from the URL.

Send it to your backend → verify_payment(reference).

Backend calls Paystack verify API → Paystack responds with "status": "success" or "failed".

Backend updates the Payment record in your DB.		

Backend returns the result to your frontend.


🔹 3. Showing success or failed

Now React has the verification result:

If backend says "success" → show PaymentDetails page (receipt, order info).

If backend says "failed" → redirect/show FailedPayment page.

So yes, exactly like you said:
👉 user pays → Paystack redirects back to your frontend → your frontend calls backend to verify → if success show success page else failed page.

---------------------------------------------------------------

👋👋 We have now written the views, The initialize payment, verify_payment, paystack_Webhook, paystack_callback view --> see views.py

we've added to the routes to the urls.py --> see urls.py
---- 
now for us to test it out see if it works(moment of truth)

--> first, we need to fetch data from the backend for the Checkout.jsx page

we'll fetch the order_id, amount to the frontend

--------------------------------

first we try to get the session_id of the user and use it to find the user's order

then we calc the total price of the order:
        # ✅ Use OrderItem.price instead of Product.price
        total_price = sum(item.price * item.quantity for item in order.items.all())
then we send as json the order_id and the total price to the frontend
see the rest of the code in views.py -> class CheckoutSummary(APIView):

--------------------------------------------------------------
Now i want to build a cancel order feature where in the checkout.jsx page the user can cancel the order, once the user cancels the order, the user is directed to the very home page
-----------------------------------------------------------------

Notes ---- on the cancel order feature. explain: -> Since we can't override Orders, we have to provide a way for the user to choose: that is why we came up with the cancel order feature in the checkout.jsx page:

we use the order id which is uuid to pinpoint the order exactly that the user wants to delete and once we delete we redirect the user back to the home '/'

class CancelOrder(generics.DestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = "pk"

the lookup field also works for uuid, in the urls.py, we also add a `/<uuid:pk>/` initially we had errors because we assumed it should be `/<int:pk>/`

We also refactored the InitializePayment view --> see views.py
---------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>

✅ This view’s job is simple:
👉 When someone clicks “Pay Now” on your site, this view talks to Paystack and sets up that payment.
👉 It tells Paystack things like: who is paying (email), how much, and what order it belongs to.
👉 If Paystack says “Cool, I’ve created a payment link!”, we also record that attempt in our own database as a Payment with status “pending”.

  CODE EXPLANATION


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

-------------------------
We get the order_id, email and amount, and then send it to the backend,
The backend interacts with the paystacks api and initializes the payment procedure

`order = get_object_or_404(Order, id=order_id)`
This checks for the order in the database if it exists, then we continue.
else, we send an error message of 'Not found'

` reference = str(uuid.uuid4())` -> we generate a unique reference for the payment
Think of it like a secret tracking number for Paystack + our database.

` headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}`
paystack wants to confirm we are who we say we are, so we pass in our SECRET_KEY
think of it as showing your id card

`        data = {
            "reference": reference,
            "email": email,
            "amount": int(amount * 100)  # convert to kobo
        }
`

we prepare our data. Also, note that paystack works in kobo that amount-in-naira * 100

`        try:
            response = requests.post(
                "https://api.paystack.co/transaction/initialize",
                headers=headers,
                data=data,
                timeout=10
            )
            res_data = response.json()
`

We now “call Paystack” via the internet.

We send them the data, and they reply with JSON.

Example response might include: `res_data = response.json()`

{
  "status": true,
  "message": "Authorization URL created",
  "data": {
      "authorization_url": "https://checkout.paystack.com/abc123",
      "access_code": "abc123",
      "reference": "a12f98c3-..."
  }
}

If something goes wrong, like no internat connection, we send a network error in the exceptions block


        if res_data.get('status') is True:
            Payment.objects.create(
                order = order,
                email = email,
                amount = amount,
                reference = reference,
                status ='pending'
            )
            return Response(res_data, status=200)

If Paystack says everything is fine:

We create a Payment record in our DB with status pending.

Pending = “The payment has started, but we don’t know if it succeeded yet.”

We then return Paystack’s response to the frontend.

The frontend will use the authorization_url Paystack gave us to redirect the user to Paystack’s checkout page.


-- if it fails we return a msg saying the payment init failed


------------------

The paystack_callback view:  -> see views.py ----->

✅✅ What the callback does (big picture)

After the customer pays on Paystack, Paystack sends them back to your site (to this callback URL) with a reference in the URL.

Your server uses that reference to ask Paystack: “Did this payment actually succeed?”

If Paystack says yes, you mark the payment as success in your database and redirect the user to your React page that shows “Payment Successful”.

If Paystack says no, you mark it as failed and redirect to “Payment Failed”.

Think of the reference as the transaction’s unique tracking number


-------------------
The paystack_webhook view -> 
Think of the webhook as the source of truth the look at this for absolute proof that the particular user has paid

Webhook is different — Paystack’s servers will send a background POST request to your server to inform you about payment events (success, failure, refunds, etc.), even if the user never returns to your site.

👉 The webhook is the most trustworthy source of truth for payment status, so it’s important that it’s clean, secure, and idempotent (handles duplicates gracefully).

see the views.py
------------------------------------

CODE EXPLANATION: 

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
------------------

What's the paystack webhook again, 

--> The webhook is paystack's way of telling our backend whether truly a payment is successful or not

its like our source of truth:

the `@csrf_exempt tells django to not require a csrf token because paystack is not a user `

payload = request.body
signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE", "")

Grab the raw message and Paystack’s “stamp”
payload = the exact bytes Paystack sent (the JSON body).

signature = a special header Paystack includes, like a tamper-proof stamp that proves they sent it.

Next: Recreate the stamp and compare, we need to know for sure its paystack interacting with us

expected_signature = hmac.new(
    key=settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
    msg=payload,
    digestmod=hashlib.sha512
).hexdigest()

if signature != expected_signature:
    return HttpResponse(status=400)

`$We use our secret key and the exact payload to recompute what the signature should be.

If our result doesn’t match the header Paystack sent, we reject the request.$`

`event = json.loads(payload)` -> We turn the json into a python dicts. like this: 

{
  "event": "charge.success",
  "data": {
    "reference": "abc-123",
    "amount": 150000,  # kobo
    ...
  }
}

if json is broken, we return 404 

---

event_type = event.get("event")
data = event.get("data", {})
reference = data.get("reference")
if not reference:
    return HttpResponse(status=400)
--------------

event_type could be "charge.success" or "charge.failed".

reference is the unique payment ID that you also stored when you started the payment.

No reference? We can’t match anything in our DB → reject.
----


Next we find our payment in the database:

`payment = Payment.objects.get(reference=reference)`
Looks up your Payment row that has the same reference.

If we can’t find it, reject (maybe someone sent a fake ref).

------------------------
If Paystack says success, verify the money and save

if event_type == "charge.success":
    if int(data.get("amount", 0)) == int(payment.amount * 100):
        payment.status = "success"
        payment.paid_at = data.get("paid_at")
        payment.save()


Paystack sends amounts in kobo (₦1,500 = 150000), but you probably store naira (e.g., 1500).
So we multiply your amount by 100 and make sure they match.
This stops anyone from paying less and pretending it’s full payment.

If amounts match, we mark the payment success and save the time.


if the event_type == 'charge.failed'

we set the payment.status to failed
and also save it to the database

`return HttpResponse(status=200)`
Always return 200 OK so Paystack won’t keep retrying the same webhook.
------------------------------------

------------------------

The paystack callback view:  CODE EXPLANATION

What the callback does (big picture)

After the customer pays on Paystack, Paystack sends them back to your site (to this callback URL) with a reference in the URL.

Your server uses that reference to ask Paystack: “Did this payment actually succeed?”

If Paystack says yes, you mark the payment as success in your database and redirect the user to your React page that shows “Payment Successful”.

If Paystack says no, you mark it as failed and redirect to “Payment Failed”.

This is a Django view function. Django calls it when Paystack redirects the user back to your site.

`reference = request.GET.get("reference")`

paystack sends the user a url
so we grab the reference from that very url

if there is no reference, we send an error:

`headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
url = f"https://api.paystack.co/transaction/verify/{reference}"`

To check if the payment is real, we call Paystack’s Verify Transaction API.

We add your secret key in the header so Paystack knows it’s really you.


response = requests.get(url, headers=headers, timeout=10)
result = response.json()
We call Paystack’s verify endpoint.

result is paystack's answer in json: a python dict:  example: 

{
  "status": true,
  "data": {
    "status": "success",
    "amount": 1250000,   // in kobo
    "paid_at": "2025-08-26T17:20:00Z",
    "reference": "abc-123-xyz"
  }
}


`if result.get("status") and result["data"]["status"] == "success":`

from the example python dict above try to reason with this if statement

Two checks: 
Paystack’s API call worked (status is true).

The actual payment inside data is marked "success".

`payment = Payment.objects.get(reference=reference)`

we find the payment record in the database,  if it does not exists? we give an error and also
update the payment database: payment.status = 'failed'

we also double check and verify if the amount truly matches:

            if int(payment.amount * 100) != result['data']['amount']:
                logger.warning("⚠️ Payment amount mismatch in Paystack callback")
                return redirect(f"{settings.FRONTEND_BASE_URL}/payment/failed/{reference}")
  if it does not, treat as an error

we then save to the database:

            payment.status = 'success'
            payment.paid_at = result['data'].get('paid_at')
            payment.save()

`return redirect(f"/payment-details/{reference}?status=success")`
-> we then send the user to our react route on the frontend





--------------------

---------
---------


There is this disturbing bug we had" --> -----> 📍📍🧧🧧

Lets say a user (Bob) adds some items to cart and the subtotal is #30,000- > he then clicks on 'proceed to checkout' btn and them, in the Checkout.jsx page, he sees the order_id, and the total price (#30,000)

lets say bob pays for this in the paystack  and all is complete

Then, Bob decides to go back to the homepage and purchase another , lets say 27,000 then proceeds to checkout

in the checkout page the BUG manifests -> bob sees 0.00 total price and no order id

This happens because the initial order bob has of 30,000 is intefering with this new purchase he wants to make

-----------------
        FIX

Purpose: make sure there are no old Pending orders hanging around that could confuse the checkout flow. Only one new pending order should remain after this runs.

i think the first order bob made is still set to 'pending' so we should either deem it as 'cancelled'  or 'paid'

either way the order cannot stay pending the order has to make way for other ordes Bob does

so in the Proceed to Checkout view, on the backend, 
after the subtotal calc-> we say: 

            if user:
                prev_pending = Order.objects.filter(user=user, status='pending')
            else:
                prev_pending = Order.objects.filter(session_id=session_id, status='pending')
            
            if prev_pending.exists():
                # Bulk update previous pending orders to 'cancelled' so they don't interfere.
                prev_pending.update(status='cancelled')

that's if the user has not paid for the previous order -> TAKE NOTE
if the user has paid the status will be set tp 'paid' if not: cancelled


✅✅ But we found out that the code fix above can cause race conditions so we change it a bit

if tow users click on the 'proceed to checkout' at the same time, race conditions could occur,
this could byoass  the _ if prev_pending.exists():
causing duplicates, so fix, we go atomic: 

from django.db import transaction

with transaction.atomic():
    # lock the cart row to prevent concurrent checkout for same cart
    if user:
        prev_pending = Order.objects.filter(user=user, status='pending')
    else:
        prev_pending = Order.objects.filter(session_id=session_id, status='pending')

    # optional: ignore orders that have a payment with status 'pending' (so we don't cancel an in-progress payment)
    prev_pending = prev_pending.exclude(payments__status='pending')

    # bulk mark as cancelled (fast)
    prev_pending.update(status='cancelled')

    # now create new order safely inside same transaction
    order = Order.objects.create(...)

there by locking it making it one user at a time the first user clicks, then the second user can click
win/win



---------------------------------
In the CheckoutSummary view, we send to the frontend, (in the Checkout.jsx)

the latest order the user made to the frontend

        if session_id:
            order = Order.objects.filter(session_id=session_id, status='pending').order_by("-created_at").first()
        if not order:
            print("🧧 Order in checkoutSummary not found")
            return Response({"error": "No active order found"}, status=404)
`The order_by() means we filtering the order by the one the user recently created this stops the logic or the backend from getting confused-> The backend sends the latest one to the the frontend`

-------------------
Next, we go to the verifed payment view

after the payment.save()

we set the order that have been paid for to 'paid' not pending
we set the order to payment.order:

    try:
        order = payment.order
        order.status = 'paid'
        order.save()
    except Exception:
        logger.exception("Failed to update order status after payment verify")

Then, we mov to the webhook view and after, the callback view: 

        try:
            order=  payment.order
            order.status = 'paid'
            order.save()
        except Exception:
            logger.exception("Failed to update order status in webhook")

and set the order to payment.order, the order.status to 'paid'

--✅  That's how we solved the bug



--==--====---=--=-=-=-=--=-==-=--=0-=-=-=--=-=-=
Next we want to create a MyOrders page on the frontend, where user can view what they've ordered.

We're keepin things simple, 

The frontend design will be like a section
in each section, we fetch the order_id, total_price, and the status

so if a user for example has 3 orders

each order of course will contain order_id, total_price, status

we'll write some sort of nore below the components saying, 'we shall communicate with you via email, phone number' or so

🧧 wait, are we to fetch from the payment model or order model?

i tried writing the code and i came up with 2 methods: 

# class ListMyOrder(generics.ListAPIView):
#     def get_order_details(self, request):
#         queryset = Order.objects.all()
#         serializer_class = OrderSerializer

class GetUserOrder(APIView):
    def get_order_details(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({
                "error": "Session_id is required"
            })
        if session_id:
            order = Order.objects.get(session_id=session_id)
        else:
            return Response({"error": "Order not found"})
        return Response({
            "id": order.id,
            "total_price": order.total_price,
            "status": order.status
        })
Which should we use? Help me with the code 



We did a MyOrders feature where users can view what orders they have

see views.py and MyOrders.jsx



        -------------  DEPLOYMENT PHASE ---------------


So, we finally reached this stage huh, we using render to deploy the app, it will be a demo like version at start, but lets see if we can upload the live version later

so we moved the .env file to the outer backend folder, we changed a few things in the settings.py

we installed more packages eg, gunicorn, whitenoise, which will be needed for the deployment

we used the command `pip freeze > requirements.txt` to create the requirements.txt

after we create a Procfile in the outer backend dir and add this inside the file

"web: gunicorn backend.wsgi:application"

next, we push to github next

recall we also made some changes in the settings.py file, since we've installed whitenoise, among other things
we need to add this in the middlewareSection in settngs.py:   "whitenoise.middleware.WhiteNoiseMiddleware",

also created a static dir in the outer backend dir, and inside it we created a products dir which contains all the product images (we copied all the images in the media dir to it)

also in the settings.py: we added this:

STATICFILES_DIRS = [BASE_DIR / "static"]   # where your source static (static/products/...) lives
STATIC_ROOT = BASE_DIR / "staticfiles"     # collectstatic will output here

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

we also added the react-vite frontend url in the ALLOWED_HOSTS section => 

then in the urls.py section, in the inner backend dir, we say: 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]

# Serve media and static in development (only when DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


then we ran this code: `python collectstatic --noinput`

this created a staticfiles dir inside it contains admin dir, products dir (which contains our product images)

we will use the static/products/'images' in production we'll ignore the media dir and staticfiles dir


we also created a static_image json for us to send to the frontend,

recall in the frontend, when we say `product.img` => this is referring to the media dir
so we need to change that and configure it to fetch from the static dir

so in the serializers.py under the ProductSerializer:  we say:

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


in the `def get_static_image` -> lets explain it:

the general idea is to create a json static_image, so we configure the program to fetch from the static dir

`i will explain later`


so in the frontend, change product.img => product.static_image wherever neccessary

----------------------------------------


So what nect?
in the settings.py change the DATABASE to this:

DATABASES = {
    "default": env.db(
        "DATABASE_URL",  # Render will provide this in production
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"  # fallback for local dev
    )
}

this will help us when we want to configure postgres on render


next we push to github

we successfully pushed the backend side of things to github

-- lets move to push the frontend side of things














😘😘✅✅ Do not forget to configure BACKEND_BASE_URL on render
Small tips to remember

Make sure collectstatic runs on deploy so /static/products/<filename> actually exists on the server.

DRF viewsets normally pass request automatically — so in most API responses you’ll get full absolute URLs out-of-the-box.

Set BACKEND_BASE_URL env var on Render as a safety net for contexts without request.




















