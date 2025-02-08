from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Book, Cart, Author,Order,OrderItem

# Register your models here.

class CustomUserAdmin(UserAdmin):
    # Customize the admin panel fields if necessary
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('profile_picture', 'location', 'phone',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name')
   
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username', )

admin.site.register(User, CustomUserAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id','name', 'description')
    search_fields = ('name', 'description')
    list_filter = ('name', )
    save_on_top = True
    # readonly_fields = ('description', )
    # exclude = ('description', )
    # fields = ('description', 'name')
    # fieldsets = (
    #     ('Category Information', {'fields': ('name',)}),
    #     ('Description', {'fields': ('description',), 'classes': ('collapse',)}),
    # )
    # actions = ['mark_published', 'archive_categories']

    # def mark_published(self, request, queryset):
    #     queryset.update(status='published')

    # def archive_categories(self, request, queryset):
    #     queryset.update(status='archived')

    # prepopulated_fields = {'description': ('name', )}
    list_per_page = 10

admin.site.register(Category, CategoryAdmin)

admin.site.register(Book)
admin.site.register(Author)

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
