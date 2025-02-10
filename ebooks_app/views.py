from django.shortcuts import render,get_object_or_404,redirect
from .models import Category,Book,Author,Cart, CartItem,Order,Payment
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from django.contrib.auth import logout as auth_logout,  login as auth_login,authenticate
from django.contrib import messages
from .forms import  RegisterForm, UpdateProfileForm
from .models import Order
from .models import Order, Cart,OrderItem
from django.contrib.auth.decorators import login_required
import json
import razorpay
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from .forms import EnquiryForm, ContactForm

from django.core.paginator import Paginator
# Create your views here.
def home(request):
    categories = Category.objects.all()
    trending_books = Book.objects.filter(is_trending=True)
    new_arrival_books = Book.objects.all().order_by('-added_on')[:10]
    best_seller_books = Book.objects.filter(is_best_seller=True)

    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            # Display success message
            messages.success(request, "Your enquiry has been submitted successfully!")
            return redirect('home')  # Redirect back to the home page
        else:
            # Display failure message
            messages.error(request, "There was an error submitting your enquiry. Please try again.")
            return redirect('home')  # Redirect back to the home page
    else:
        form = EnquiryForm()

    return render(request, "pages/home.html", {
        "categories": categories,
        "trending_books": trending_books,
        "new_arrival_books": new_arrival_books,
        "best_seller_books": best_seller_books,
        "form": form
    })

def books(request, id=None):
    filter_type = request.GET.get('filter', 'all')
    books = Book.objects.all()  # Default queryset
    category_name = None

    # Handle filter types
    if filter_type == 'trending':
        books = books.filter(is_trending=True)
        category_name = "Now Trending"
    elif filter_type == 'new_arrivals':
        books = books.order_by('-added_on')
        category_name = "New Arrivals"
    elif filter_type == 'best_sellers':
        books = books.filter(is_best_seller=True)
        category_name = "Best Sellers"

    # Handle category filtering
    if id:
        category = get_object_or_404(Category, category_id=id)
        books = books.filter(category=category)
        # Combine category name with filter name (if applicable)
        category_name = f"{category.name} - {category_name}" if category_name else category.name

    # Pagination setup
    page_number = request.GET.get('page', 1)  # Get the page number from the request
    paginator = Paginator(books, 20)  
    page_obj = paginator.get_page(page_number)

    # Prepare context
    context = {
        'category': category_name or "All Books",  # Fallback to "All Books" if no category
        'books': page_obj,  # Paginated book list
    }

    return render(request, "pages/books.html", context)

def book(request,id):
    book=get_object_or_404(Book,Book_id=id)
    related_books = Book.objects.filter(category=book.category).exclude(Book_id=id)
    return render(request, "pages/book.html", {"book":book,"related_books":related_books})

@login_required
def update_profile(request):
    user = request.user  # Get the logged-in user

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')  # Redirect back to the same page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UpdateProfileForm(instance=user)  # Pre-fill the form with user's data

    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    context = {
        'form': form,
        'orders': orders
    }
    return render(request, "pages/profile.html",context)
def order_success(request):
    return render(request, "pages/order_success.html")


def authors(request):
    # Get authors with the count of books written
    authors = Author.objects.annotate(
        book_count=Count('book')  # Count the number of books per author
    )

    # Prepare data for template
    data = []
    for author in authors:
        # Get distinct categories and their book counts for the author
        categories = (
            Book.objects.filter(author=author)
            .values('category__name')
            .annotate(category_count=Count('category'))
            .order_by('-category_count')  # Sort categories by book count
        )

        # Find the top category (if any)
        top_category = categories[0]['category__name'] if categories else None

        data.append({
            'author': author,
            'book_count': author.book_count,
            'categories': [cat['category__name'] for cat in categories],  # All categories
            'top_category': top_category,  # Top category
        })

    # Pagination setup
    page_number = request.GET.get('page', 1)
    paginator = Paginator(data, 12)  # Show 10 authors per page
    page_obj = paginator.get_page(page_number)

    return render(request, "pages/authors.html", {"authors": page_obj})

def author(request,id):
       # Fetch the author object
    author = get_object_or_404(Author, id=id)

    # Fetch books written by the author
    books = Book.objects.filter(author=author)

    # Determine the category the author is famous for
    top_category = (
        books.values('category__name')  # Group by category name
        .annotate(book_count=Count('Book_id'))  # Count books in each category
        .order_by('-book_count')  # Sort by book count descending
        .first()  # Get the first (top) category
    )

    # Prepare context
    context = {
        'author': author,
        'books': books,
        'top_category': top_category['category__name'] if top_category else None,
    }
    return render(request, "pages/author.html", context)

def about(request):
    return render(request, "pages/about.html")

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your enquiry has been submitted successfully!")
            return redirect('contact')  # Redirect to the same contact page after successful submission
        else:
            messages.error(request, "There was an error with your submission. Please try again.")
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {'form': form})


@login_required(login_url='/login/') 
def add_to_cart(request, book_id):
    book = get_object_or_404(Book, Book_id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    # Check if the book is already in the cart
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        cart_item.quantity += 1  # Increment quantity if already exists
        cart_item.save()
    return redirect('view_cart')

@login_required(login_url='/login/') 
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@login_required(login_url='/login/') 
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()  # Remove item if quantity is 0
    return redirect('view_cart')

@login_required(login_url='/login/') 
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    quantity_range = range(1, 11)  # Generate numbers from 1 to 10
    return render(request, 'pages/view_cart.html', {'cart': cart,"quantity_range": quantity_range})

def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Use the email as the username for authentication
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')

    return render(request, 'pages/auth/login.html', {})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')  # Replace 'login' with the name of your login route
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RegisterForm()

    return render(request, 'pages/auth/signIn.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('home')

 
@login_required
def user_orders(request):
    # Retrieve all orders for the logged-in user
    
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'pages/user_orders.html', {'orders': orders})

@login_required(login_url='/login/') 
def order_detail(request, order_id):
    # Retrieve a specific order for the logged-in user
    order = get_object_or_404(Order, id=order_id)
    order_items = order.order_items.all()
    return render(request, 'pages/order_detail.html', {'order': order, 'order_items': order_items})


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

MIN_ORDER_AMOUNT = 100  # Minimum order amount in INR

@login_required(login_url='/login/')
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)

    # Check if the user has a phone number
    if not request.user.phone or not request.user.location:
        # If phone number or address is missing, redirect to profile page with a message
        messages.warning(
            request,
            "Please complete your profile by adding your phone number and address before proceeding to checkout."
        )
        return redirect("profile") 

    cart_total_price = cart.get_total_price()  # Cart total in INR
    
    if cart_total_price < MIN_ORDER_AMOUNT:
        messages.error(
            request,
            f"Your order total is ₹{cart_total_price:.2f}, which is less than the minimum allowed amount of ₹{MIN_ORDER_AMOUNT}. Please add more items to your cart."
        )
        return redirect("view_cart")

    if request.method == "GET":
        amount_in_paisa = int(cart_total_price * 100)

        razorpay_order = razorpay_client.order.create({
            "amount": amount_in_paisa,
            "currency": "INR",
            "payment_capture": 1
        })

        context = {
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "amount": amount_in_paisa,
            "currency": "INR",
            "razorpay_order_id": razorpay_order["id"],
            "cart": cart,
            "user": request.user,
        }

        return render(request, "pages/checkout.html", context)

def create_order(user, cart, payment_data):
    cart_items = CartItem.objects.filter(cart=cart)

    # Create the order
    order = Order.objects.create(
        user=user,
        total_amount=cart.get_total_price(),
        status='pending',
        shipping_address=user.location,  # Customize based on your model
        receipt_id=payment_data['razorpay_payment_id'],
        razorpay_payment_id=payment_data['razorpay_payment_id'],
    )

    # Add items to the order
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            book=cart_item.book,
            quantity=cart_item.quantity
        )

    # Clear the cart
    cart.items.all().delete()

    return order

@login_required(login_url='/login/')
def verify_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            razorpay_client.utility.verify_payment_signature({
                "razorpay_order_id": data["razorpay_order_id"],
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_signature": data["razorpay_signature"]
            })

            cart = get_object_or_404(Cart, user=request.user)

            payment_data = {
                "razorpay_payment_id": data["razorpay_payment_id"],
                "razorpay_order_id": data["razorpay_order_id"],
            }
            order = create_order(request.user, cart, payment_data)

            return JsonResponse({"status": "success"})

        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"status": "Payment verification failed!"}, status=400)

    return JsonResponse({"status": "Invalid request"}, status=400)