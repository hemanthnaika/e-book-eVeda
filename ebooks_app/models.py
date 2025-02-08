from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Email as a unique identifier
    username = models.CharField(max_length=150, blank=True, null=True)  # Make username optional
    profile_picture = models.ImageField(upload_to='user_profiles/', blank=True, null=True)  # Profile picture
    location = models.CharField(max_length=255, blank=True, null=True)  # User location
    phone = models.CharField(max_length=10, blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email  # Use email for string representation

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Author(models.Model):
    first_name = models.CharField(max_length=100)  # Author's first name
    last_name = models.CharField(max_length=100)   # Author's last name
    bio = models.TextField(blank=True, null=True)  # Short biography
    date_of_birth = models.DateField(blank=True, null=True)  # Date of birth
    date_of_death = models.DateField(blank=True, null=True)  # Date of death (optional)
    website = models.URLField(blank=True, null=True)  # Author's website
    photo = models.ImageField(upload_to='author_photos/', blank=True, null=True)  # Author's photo

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name='Author'
        verbose_name_plural='Authors'
        ordering = ['last_name', 'first_name']  # Order by last and first name
        
class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    logo = models.CharField(max_length=50, blank=True, null=True)
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):  # Fix here
        return self.name



class Book(models.Model):
    Book_id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    description = models.TextField()
    published_date = models.DateField()
    price = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Draft'), ('published', 'Published')],
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True)
    # Additional fields to track book status
    is_trending = models.BooleanField(default=False)  # For trending books
    is_best_seller = models.BooleanField(default=False)  # For best sellers
    added_on = models.DateTimeField(default=timezone.now)  # Date when book is added to the store
    sales_count = models.PositiveIntegerField(default=0)  # To track sales for best sellers

    def __str__(self):
        return self.title
    
    
# Cart
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all()) 


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    

    def __str__(self):
        return f"{self.quantity} of {self.book.title}"

    def get_total_price(self):
        return self.book.price * self.quantity
    
    
class OrderItem(models.Model):
    order = models.ForeignKey('Order', related_name='order_items',on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.book.title}"

    def get_total_price(self):
        return self.book.price * self.quantity
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(Book, through='OrderItem')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    shipping_address = models.TextField()
    receipt_id = models.CharField(max_length=255, blank=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Order #{self.user.username}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=50, choices=[('success', 'Success'), ('failed', 'Failed')])
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)
    
    
class Enquiry(models.Model):
    class Meta:
        verbose_name_plural = 'Enquiries'

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    message = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Contact(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Contact'

    def __str__(self):
        return f"Enquiry from {self.first_name} {self.last_name}"