from django.contrib import admin
from .models import Product


# Product admin setup for quick catalogue management.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Columns shown in the product list.
    list_display = ("name", "price", "is_active")

    # Enables search by product name.
    search_fields = ("name",)

    # Sidebar filter for active/inactive products.
    list_filter = ("is_active",)

