import random
import uuid
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone
from ebooks_app.models import User, Author, Category, Book, Cart, CartItem, Order

fake = Faker()

# Function to fetch a random image from the internet
def fetch_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"{uuid.uuid4()}.jpg")
    except Exception as e:
        print(f"Failed to fetch image: {e}")
    return None

class Command(BaseCommand):
    help = "Generate fake data for the database"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Generating Fake Data..."))

        # Create Users
        users = []
        for _ in range(5):
            user = User.objects.create(
                username=fake.user_name(),
                email=fake.unique.email(),
                phone=fake.phone_number()[:10],
                location=fake.city(),
                is_admin=fake.boolean(),
            )
            # Fetch profile picture
            user.profile_picture.save(
                f"{user.username}.jpg", fetch_image("https://picsum.photos/200")
            )
            users.append(user)

        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} Users."))

        # Create Authors
        authors = []
        for _ in range(5):
            author = Author.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.text(),
                date_of_birth=fake.date_of_birth(minimum_age=30, maximum_age=80),
                date_of_death=fake.date_between(start_date="-10y", end_date="today")
                if random.choice([True, False])
                else None,
                website=fake.url(),
            )
            # Fetch author photo
            author.photo.save(
                f"{author.first_name}_{author.last_name}.jpg",
                fetch_image("https://loremflickr.com/300/400/portrait"),
            )
            authors.append(author)

        self.stdout.write(self.style.SUCCESS(f"Created {len(authors)} Authors."))

        # Create Categories
        categories = []
        for _ in range(5):
            category = Category.objects.create(
                name=fake.word().capitalize(),
                description=fake.text(),
                logo=fake.word(),
            )
            categories.append(category)

        self.stdout.write(self.style.SUCCESS(f"Created {len(categories)} Categories."))

        # Create Books
        books = []
        for _ in range(10):
            book = Book.objects.create(
                title=fake.sentence(nb_words=4),
                author=random.choice(authors),
                description=fake.text(),
                published_date=fake.date_between(start_date="-5y", end_date="today"),
                price=random.randint(100, 2000),
                status=random.choice(["draft", "published"]),
                category=random.choice(categories),
                is_trending=random.choice([True, False]),
                is_best_seller=random.choice([True, False]),
                sales_count=random.randint(0, 500),
            )
            # Fetch book cover image
            book.cover_image.save(
                f"{book.title}.jpg",
                fetch_image("https://loremflickr.com/300/400/book"),
            )
            books.append(book)

        self.stdout.write(self.style.SUCCESS(f"Created {len(books)} Books."))

        # Create Carts and CartItems
        for user in users:
            cart = Cart.objects.create(user=user)
            for _ in range(random.randint(1, 3)):  # 1-3 items per cart
                CartItem.objects.create(
                    cart=cart, book=random.choice(books), quantity=random.randint(1, 5)
                )

        self.stdout.write(self.style.SUCCESS(f"Created Carts & Cart Items."))

        # Create Orders
        for user in users:
            if random.choice([True, False]):  # 50% chance to create an order
                Order.objects.create(
                    user=user,
                    total_amount=random.uniform(200, 5000),
                    status=random.choice(["pending", "completed"]),
                    shipping_address=fake.address(),
                    receipt_id=str(uuid.uuid4()),
                    razorpay_payment_id=str(uuid.uuid4()),
                )

        self.stdout.write(self.style.SUCCESS("Fake Data with Images Generated Successfully!"))
