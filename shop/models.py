from django.db import models


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