from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0008_seed_client_price_list_products"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariant",
            name="qty_in_stock",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
