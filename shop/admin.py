from django.contrib import admin
from .models import Order, OrderItem, Product, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ("strength", "price", "qty_in_stock", "is_active")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "is_accessory", "is_active", "starting_price")
    search_fields = ("name",)
    list_filter = ("is_accessory", "is_active")
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "strength", "price", "qty_in_stock", "is_active")
    search_fields = ("product__name", "strength")
    list_filter = ("is_active",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "email", "total_amount", "status", "town_or_city", "postcode", "created_at")
    search_fields = ("reference", "email")
    list_filter = ("status", "created_at")
    readonly_fields = ("reference", "total_amount", "created_at")

    fieldsets = (
        (None, {
            "fields": ("reference", "email", "name", "total_amount", "status", "created_at")
        }),
        ("Shipping address", {
            "classes": ("collapse",),
            "fields": ("address_line_1", "address_line_2", "town_or_city", "county", "postcode", "country"),
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "variant", "unit_price", "quantity", "line_total")
    search_fields = ("order__reference", "product__name", "variant__strength")

