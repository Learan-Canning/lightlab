from decimal import Decimal

from django.db import migrations


def apply_client_updates(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    ProductVariant = apps.get_model("shop", "ProductVariant")

    hidden_product_names = [
        "Research Supply Bundle",
        "Pack of 10 Needles (29G x 12.7mm)",
        "Pack of 10 Sterile Needles and Syringes",
        "Pack of 20 Sterile Alcohol Wipes",
        "10ml Bacteriostatic Water Vial (0.9% Benzyl Alcohol)",
    ]
    for name in hidden_product_names:
        Product.objects.filter(name__iexact=name).update(is_active=False)

    bac_product, _ = Product.objects.get_or_create(
        name="10ml BAC Water 0.9% Benz",
        defaults={
            "description": "Bacteriostatic water (0.9% benzyl alcohol) for reconstitution of research peptides in laboratory settings.",
            "price": Decimal("5.00"),
            "is_active": True,
            "is_accessory": True,
        },
    )
    bac_product.description = "Bacteriostatic water (0.9% benzyl alcohol) for reconstitution of research peptides in laboratory settings."
    bac_product.price = Decimal("5.00")
    bac_product.is_active = True
    bac_product.is_accessory = True
    bac_product.save(update_fields=["description", "price", "is_active", "is_accessory"])

    bac_variant, _ = ProductVariant.objects.get_or_create(
        product=bac_product,
        strength="10ml",
        defaults={"price": Decimal("5.00"), "is_active": True},
    )
    bac_variant.price = Decimal("5.00")
    bac_variant.is_active = True
    bac_variant.save(update_fields=["price", "is_active"])

    non_alcohol_product, _ = Product.objects.get_or_create(
        name="10ml Bacteriostatic Water (Non-Alcohol)",
        defaults={
            "description": "Sterile 10ml non-alcohol bacteriostatic water for laboratory reconstitution workflows.",
            "price": Decimal("5.00"),
            "is_active": True,
            "is_accessory": True,
        },
    )
    non_alcohol_product.description = "Sterile 10ml non-alcohol bacteriostatic water for laboratory reconstitution workflows."
    non_alcohol_product.price = Decimal("5.00")
    non_alcohol_product.is_active = True
    non_alcohol_product.is_accessory = True
    non_alcohol_product.save(update_fields=["description", "price", "is_active", "is_accessory"])

    non_alcohol_variant, _ = ProductVariant.objects.get_or_create(
        product=non_alcohol_product,
        strength="10ml",
        defaults={"price": Decimal("5.00"), "is_active": True},
    )
    non_alcohol_variant.price = Decimal("5.00")
    non_alcohol_variant.is_active = True
    non_alcohol_variant.save(update_fields=["price", "is_active"])

    stock_updates = [
        ("Retatrutide", "10mg", 70),
        ("Retatrutide", "20mg", 20),
        ("Retatrutide", "30mg", 30),
        ("Retatrutide", "40mg", 20),
        ("BPC-157", "10mg", 10),
        ("TB-500", "10mg", 10),
        ("Tesamorelin", "10mg", 10),
        ("KLOW BLEND", "80mg", 10),
        ("MOTS-c", "10mg", 20),
        ("BPC/TB Blend", "Standard", 10),
        ("PT-141", "10mg", 9),
        ("GHK-Cu", "50mg", 40),
        ("GHK-Cu", "100mg", 8),
        ("NAD+", "1000mg", 8),
        ("Melanotan II", "10mg", 25),
    ]

    for product_name, strength, qty in stock_updates:
        variant = ProductVariant.objects.filter(
            product__name__iexact=product_name,
            strength__iexact=strength,
        ).first()
        if not variant:
            continue
        variant.qty_in_stock = qty
        variant.is_active = True
        variant.save(update_fields=["qty_in_stock", "is_active"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0009_productvariant_qty_in_stock"),
    ]

    operations = [
        migrations.RunPython(apply_client_updates, noop_reverse),
    ]
