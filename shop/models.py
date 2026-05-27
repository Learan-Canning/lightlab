from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4


# Product model used by the homepage shop section.
class Product(models.Model):
    # Core product details.
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    # Default text shown if no custom description is entered.
    description = models.TextField(
        default="This is a synthetic research chemical supplied as lyophilized powder. Third-party tested at 99%+ purity. For laboratory research use only."
    )

    # Optional image uploaded in Django admin.
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    # Lets you hide a product without deleting it.
    is_active = models.BooleanField(default=True)

    # Admin and shell string representation.
    def __str__(self):
        return self.name

  
def _generate_reference():
    return uuid4().hex[:12].upper()

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
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} — {self.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.line_total = (Decimal(self.unit_price) * Decimal(self.quantity)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} x{self.quantity} — {self.order.reference}"