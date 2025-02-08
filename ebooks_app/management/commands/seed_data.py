from django.core.management.base import BaseCommand
from django.utils import timezone
from ebooks_app.models import User, Author, Category, Book, Cart, CartItem
from faker import Faker
import random
from django.core.files.base import ContentFile
import requests

class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Helper function to fetch a fake image
        def fetch_fake_image():
            response = requests.get("https://picsum.photos/200/300", stream=True)
            if response.status_code == 200:
                return ContentFile(response.content, name=f"{fake.word()}.jpg")
            return None

        # Create Users
        users = []
        for _ in range(50):
            users.append(User.objects.create_user(
                email=fake.unique.email(),
                username=fake.user_name(),
                password="password123",
                profile_picture=fetch_fake_image(),
                location=fake.city(),
                phone=fake.msisdn()[:10],
                is_admin=False
            ))

        # Create Authors
        authors = []
        for _ in range(50):
            authors.append(Author.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                bio=fake.text(max_nb_chars=200),
                date_of_birth=fake.date_of_birth(minimum_age=20, maximum_age=70),
                website=fake.url(),
                photo=fetch_fake_image()
                
            ))

        # Create Categories
        categories = []
        category_names = ["Science Fiction", "Mystery", "Romance", "Adventure", "History","Fiction","Non-Fiction","Educational"]
        for name in category_names:
            categories.append(Category.objects.create(
                name=name,
                description=fake.text(max_nb_chars=100),
                logo=fetch_fake_image()
            ))

        # Create Books
        books = []
        for _ in range(100):
            books.append(Book.objects.create(
                title=fake.sentence(nb_words=3),
                author=random.choice(authors),
                description=fake.text(max_nb_chars=500),
                published_date=fake.date_between(start_date="-20y", end_date="today"),
                price=random.randint(100, 1000),
                status=random.choice(["draft", "published"]),
                category=random.choice(categories),
                cover_image=fetch_fake_image(),
                is_trending=random.choice([True, False]),
                is_best_seller=random.choice([True, False]),
                added_on=timezone.now(),
                sales_count=random.randint(0, 500)
            ))

        # Create Carts
        carts = []
        for user in users:
            carts.append(Cart.objects.create(user=user))

        # Add Items to Carts
        for cart in carts:
            for _ in range(random.randint(1, 5)):
                CartItem.objects.create(
                    cart=cart,
                    book=random.choice(books),
                    quantity=random.randint(1, 3)
                )

        self.stdout.write(self.style.SUCCESS("50 sample data entries created successfully using Faker with images!"))




# Book
# from django.core.management.base import BaseCommand
# from django.utils import timezone
# from ebooks_app.models import Author, Category, Book
# from faker import Faker
# import random
# from django.core.files.base import ContentFile
# import requests

# class Command(BaseCommand):
#     help = "Add new books using existing authors and categories"

#     def handle(self, *args, **kwargs):
#         fake = Faker()

#         # Helper function to fetch a fake image
#         def fetch_fake_image():
#             response = requests.get("https://picsum.photos/200/300", stream=True)
#             if response.status_code == 200:
#                 return ContentFile(response.content, name=f"{fake.word()}.jpg")
#             return None

#         # Get existing authors and categories
#         authors = list(Author.objects.all())
#         categories = list(Category.objects.all())

#         if not authors or not categories:
#             self.stdout.write(self.style.ERROR("Authors or Categories are missing. Add them first."))
#             return

#         # Create Books
#         books = []
#         for _ in range(50):  # Add 20 books
#             books.append(Book.objects.create(
#                 title=fake.sentence(nb_words=3),
#                 author=random.choice(authors),
#                 description=fake.text(max_nb_chars=500),
#                 published_date=fake.date_between(start_date="-20y", end_date="today"),
#                 price=random.randint(100, 1000),
#                 status=random.choice(["draft", "published"]),
#                 category=random.choice(categories),
#                 cover_image=fetch_fake_image(),
#                 is_trending=random.choice([True, False]),
#                 is_best_seller=random.choice([True, False]),
#                 added_on=timezone.now(),
#                 sales_count=random.randint(0, 500)
#             ))

#         self.stdout.write(self.style.SUCCESS(f"{len(books)} new books added successfully!"))
