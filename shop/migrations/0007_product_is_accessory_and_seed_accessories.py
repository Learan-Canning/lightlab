from decimal import Decimal

from django.db import migrations, models


RESEARCH_SUPPLY_BUNDLE_NAME = "Research Supply Bundle"


def seed_accessory_products(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    ProductVariant = apps.get_model("shop", "ProductVariant")

    accessory_data = [
        {
            "name": RESEARCH_SUPPLY_BUNDLE_NAME,
            "description": (
                "Includes 1 x 10ml Bacteriostatic Water Vial (0.9% Benzyl Alcohol), "
                "1 x Pack of 10 Sterile Needles and Syringes, and "
                "1 x Pack of 20 Sterile Alcohol Wipes."
            ),
            "price": Decimal("5.00"),
            "strength": "Bundle",
        },
        {
            "name": "10ml Bacteriostatic Water Vial (0.9% Benzyl Alcohol)",
            "description": "Sterile 10ml bacteriostatic water vial with 0.9% benzyl alcohol.",
            "price": Decimal("3.99"),
            "strength": "10ml",
        },
        {
            "name": "Pack of 10 Sterile Needles and Syringes",
            "description": "Pack of 10 sterile individually wrapped needles and syringes.",
            "price": Decimal("5.00"),
            "strength": "Pack of 10",
        },
        {
            "name": "Pack of 20 Sterile Alcohol Wipes",
            "description": "Pack of 20 sterile alcohol wipes for pre-injection preparation.",
            "price": Decimal("3.00"),
            "strength": "Pack of 20",
        },
    ]

    for item in accessory_data:
        product = Product.objects.filter(name__iexact=item["name"]).first()

        if not product:
            product = Product.objects.create(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                is_active=True,
                is_accessory=True,
            )
        else:
            fields_to_update = []

            if product.price != item["price"]:
                product.price = item["price"]
                fields_to_update.append("price")
            if not product.is_active:
                product.is_active = True
                fields_to_update.append("is_active")
            if not product.is_accessory:
                product.is_accessory = True
                fields_to_update.append("is_accessory")

            if fields_to_update:
                product.save(update_fields=fields_to_update)

        variant, _ = ProductVariant.objects.get_or_create(
            product=product,
            strength=item["strength"],
            defaults={
                "price": item["price"],
                "is_active": True,
            },
        )

        variant_updates = []
        if variant.price != item["price"]:
            variant.price = item["price"]
            variant_updates.append("price")
        if not variant.is_active:
            variant.is_active = True
            variant_updates.append("is_active")

        if variant_updates:
            variant.save(update_fields=variant_updates)


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0006_product_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_accessory",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(seed_accessory_products, migrations.RunPython.noop),
    ]
