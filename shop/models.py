from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from django.db import models


def _generate_reference():
    return uuid4().hex[:12].upper()


class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    description = models.TextField(
        default="This is a synthetic research chemical supplied as lyophilized powder. Third-party tested at 99%+ purity. For laboratory research use only."
    )
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @property
    def starting_price(self):
        active_variants = self.variants.filter(is_active=True).order_by("price")
        first_variant = active_variants.first()
        if first_variant:
            return first_variant.price
        return None


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    strength = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["product__name", "price", "strength"]
        unique_together = ("product", "strength")

    def __str__(self):
        return f"{self.product.name} - {self.strength}"


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    reference = models.CharField(max_length=24, unique=True, default=_generate_reference, db_index=True)
    email = models.EmailField()
    name = models.CharField(max_length=200, blank=True)

    address_line_1 = models.CharField(max_length=255, blank=True, default="")
    address_line_2 = models.CharField(max_length=255, blank=True, default="")
    town_or_city = models.CharField(max_length=100, blank=True, default="")
    county = models.CharField(max_length=100, blank=True, default="")
    postcode = models.CharField(max_length=20, blank=True, default="")
    country = models.CharField(max_length=100, default="United Kingdom")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} — {self.email}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = (Decimal(self.unit_price) * Decimal(self.quantity)).quantize(
            Decimal("0.01"),
            ROUND_HALF_UP,
        )
        super().save(*args, **kwargs)

    def __str__(self):
        variant_label = self.variant.strength if self.variant else "no variant"
        return f"{self.product.name} {variant_label} x{self.quantity} — {self.order.reference}"