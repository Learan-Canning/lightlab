from django.contrib import admin
from .models import Product, Order, OrderItem


# Product admin setup for quick catalogue management.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Columns shown in the product list.
    list_display = ("name", "price", "is_active")

    # Enables search by product name.
    search_fields = ("name",)

    # Sidebar filter for active/inactive products.
    list_filter = ("is_active",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Columns shown in the order list.
    list_display = ("reference", "email", "total_amount", "status", "town_or_city", "postcode", "created_at")

    # Enables search by order reference or email.
    search_fields = ("reference", "email")

    # Sidebar filter for order status and creation date.
    list_filter = ("status", "created_at")

    # Fields that are read-only.
    readonly_fields = ("reference", "total_amount", "created_at")

    # Make address fields visible in the admin detail view
    fieldsets = (
        (None, {
            'fields': ('reference', 'email', 'name', 'total_amount', 'status', 'created_at')
        }),
        ('Shipping address', {
            'classes': ('collapse',),
            'fields': ('address_line_1', 'address_line_2', 'town_or_city', 'county', 'postcode', 'country'),
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    # Columns shown in the order item list.
    list_display = ("order", "product", "unit_price", "quantity", "line_total")

    # Enables search by order reference or product name.
    search_fields = ("order__reference", "product__name")

