from django.urls import path
from . import views 
from .views import add_to_cart, remove_from_cart, update_cart, view_cart, update_profile

urlpatterns = [
    path('', views.home,name='home'),
    path('books/', views.books, name='all_books'),
    path('books/<uuid:id>/', views.books, name='books'),
    path('book/<uuid:id>/', views.book, name='book'),
    path('authors/', views.authors, name='authors'),
    path('author/<int:id>/', views.author, name='author'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', update_profile, name='profile'),
    path('order_success/', views.order_success, name='order_success'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/add/<uuid:book_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', update_cart, name='update_cart'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'), 
    path('logout/', views.logout, name='logout'),
    path("checkout/", views.checkout, name="checkout"),
    path("verify_payment/", views.verify_payment, name="verify_payment"),
    path('my-orders/', views.user_orders, name='user_orders'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]
