from decimal import Decimal

from django.db import migrations


def seed_client_products(apps, schema_editor):
    Product = apps.get_model("shop", "Product")
    ProductVariant = apps.get_model("shop", "ProductVariant")

    products = [
        {
            "name": "Semaglutide",
            "description": (
                "Synthetic peptide analogue studied in metabolic and glucose "
                "regulation research. Used in laboratory settings to investigate "
                "incretin pathways and related biochemical processes."
            ),
            "is_accessory": False,
            "variants": [
                ("5mg", Decimal("50.00")),
                ("10mg", Decimal("70.00")),
            ],
        },
        {
            "name": "Tirzepatide",
            "description": (
                "Dual-receptor agonist peptide researched for its effects on "
                "metabolic signalling pathways. Investigated in cellular and "
                "animal models for energy homeostasis and related mechanisms."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("80.00")),
                ("20mg", Decimal("120.00")),
                ("30mg", Decimal("160.00")),
            ],
        },
        {
            "name": "Retatrutide",
            "description": (
                "Triple-agonist peptide studied in metabolic research for its "
                "interactions with multiple hormone receptors involved in "
                "energy balance and nutrient metabolism."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("80.00")),
                ("20mg", Decimal("130.00")),
                ("30mg", Decimal("180.00")),
                ("40mg", Decimal("220.00")),
            ],
        },
        {
            "name": "Cagrilintide",
            "description": (
                "Amylin receptor agonist analogue used in laboratory research "
                "exploring appetite regulation and metabolic signalling pathways."
            ),
            "is_accessory": False,
            "variants": [
                ("5mg", Decimal("60.00")),
                ("10mg", Decimal("80.00")),
            ],
        },
        {
            "name": "AOD-9604",
            "description": (
                "Fragment of growth hormone investigated in research for its "
                "potential role in lipid metabolism and fat cell regulation."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("60.00")),
            ],
        },
        {
            "name": "5-Amino-1MQ",
            "description": (
                "Small molecule compound researched for its effects on cellular "
                "metabolism and mitochondrial function in longevity and "
                "metabolic studies."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("60.00")),
            ],
        },
        {
            "name": "BPC-157",
            "description": (
                "Synthetic pentadecapeptide studied in tissue repair and "
                "regenerative research models, focusing on cytoprotective and "
                "healing mechanisms."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("50.00")),
            ],
        },
        {
            "name": "TB-500",
            "description": (
                "Thymosin Beta-4 fragment researched for its role in actin "
                "sequestration and tissue regeneration processes in laboratory "
                "models."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("55.00")),
            ],
        },
        {
            "name": "BPC/TB Blend",
            "description": (
                "Combination research blend containing BPC-157 and TB-500, "
                "studied together for synergistic effects in tissue repair and "
                "recovery models."
            ),
            "is_accessory": False,
            "variants": [
                ("Standard", Decimal("60.00")),
            ],
        },
        {
            "name": "KLOW BLEND",
            "description": (
                "Multi-peptide research blend including BPC-157, GHK-Cu, TB-500, "
                "and KPV. Investigated in laboratory settings for combined "
                "regenerative and anti-inflammatory pathways."
            ),
            "is_accessory": False,
            "variants": [
                ("80mg", Decimal("80.00")),
            ],
        },
        {
            "name": "GHK-Cu",
            "description": (
                "Copper-binding tripeptide widely studied in skin biology and "
                "extracellular matrix research for its role in collagen synthesis "
                "and tissue remodelling."
            ),
            "is_accessory": False,
            "variants": [
                ("50mg", Decimal("50.00")),
                ("100mg", Decimal("60.00")),
            ],
        },
        {
            "name": "GLOW BLEND",
            "description": (
                "Research blend containing GHK-Cu, TB-500, and BPC-157. Studied "
                "for potential combined effects on skin health and regenerative "
                "processes in laboratory models."
            ),
            "is_accessory": False,
            "variants": [
                ("70mg", Decimal("70.00")),
            ],
        },
        {
            "name": "Melanotan II",
            "description": (
                "Synthetic melanocortin analogue researched for its interactions "
                "with melanocyte-stimulating hormone receptors in pigmentation "
                "and related signalling studies."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("35.00")),
            ],
        },
        {
            "name": "NAD+",
            "description": (
                "Nicotinamide adenine dinucleotide, a critical coenzyme studied "
                "extensively in cellular energy metabolism, mitochondrial "
                "function, and aging research."
            ),
            "is_accessory": False,
            "variants": [
                ("500mg", Decimal("70.00")),
                ("1000mg", Decimal("110.00")),
            ],
        },
        {
            "name": "MOTS-c",
            "description": (
                "Mitochondrial-derived peptide investigated in longevity and "
                "metabolic research for its role in exercise mimetic effects "
                "and cellular homeostasis."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("50.00")),
            ],
        },
        {
            "name": "SS-31",
            "description": (
                "Mitochondria-targeting peptide researched for its protective "
                "effects on mitochondrial membranes and oxidative stress in "
                "cellular models."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("50.00")),
            ],
        },
        {
            "name": "Epitalon",
            "description": (
                "Synthetic tetrapeptide studied in telomere biology and cellular "
                "senescence research."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("40.00")),
            ],
        },
        {
            "name": "Pinealon",
            "description": (
                "Synthetic tripeptide researched for its potential effects on "
                "neuronal and pineal gland cell function in longevity studies."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("50.00")),
            ],
        },
        {
            "name": "Semax",
            "description": (
                "Synthetic heptapeptide analogue of ACTH studied in "
                "neuroprotection and cognitive function research models."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("50.00")),
            ],
        },
        {
            "name": "Selank",
            "description": (
                "Synthetic heptapeptide researched for its anxiolytic-like "
                "properties and effects on the central nervous system in "
                "laboratory settings."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("50.00")),
            ],
        },
        {
            "name": "DSIP",
            "description": (
                "Delta sleep-inducing peptide studied in sleep pattern and "
                "neuromodulation research."
            ),
            "is_accessory": False,
            "variants": [
                ("5mg", Decimal("40.00")),
            ],
        },
        {
            "name": "Ipamorelin",
            "description": (
                "Selective growth hormone secretagogue investigated in laboratory "
                "research for its stimulation of pituitary growth hormone release."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("50.00")),
            ],
        },
        {
            "name": "CJC-1295 (No DAC)",
            "description": (
                "Growth hormone-releasing hormone (GHRH) analogue studied for its "
                "effects on pulsatile GH secretion in endocrine research models."
            ),
            "is_accessory": False,
            "variants": [
                ("Standard", Decimal("60.00")),
            ],
        },
        {
            "name": "CJC-1295 (DAC)",
            "description": (
                "Growth hormone-releasing hormone (GHRH) analogue studied for its "
                "effects on pulsatile GH secretion in endocrine research models."
            ),
            "is_accessory": False,
            "variants": [
                ("Standard", Decimal("60.00")),
            ],
        },
        {
            "name": "Tesamorelin",
            "description": (
                "Growth hormone-releasing hormone analogue researched for its "
                "impact on GH/IGF-1 axis in laboratory settings."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("60.00")),
            ],
        },
        {
            "name": "IGF-1 LR3",
            "description": (
                "Long-acting insulin-like growth factor-1 analogue used in cell "
                "proliferation, muscle, and tissue growth research."
            ),
            "is_accessory": False,
            "variants": [
                ("1mg", Decimal("60.00")),
            ],
        },
        {
            "name": "PT-141",
            "description": (
                "Melanocortin receptor agonist peptide studied in neurological and "
                "sexual behaviour research models."
            ),
            "is_accessory": False,
            "variants": [
                ("10mg", Decimal("40.00")),
            ],
        },
        {
            "name": "Kisspeptin-10",
            "description": (
                "Metastin fragment researched for its central role in the "
                "hypothalamic-pituitary-gonadal axis and reproductive hormone "
                "regulation."
            ),
            "is_accessory": False,
            "variants": [
                ("Standard", Decimal("50.00")),
            ],
        },
        {
            "name": "LL-37",
            "description": (
                "Cathelicidin antimicrobial peptide investigated in innate immune "
                "response and antimicrobial research."
            ),
            "is_accessory": False,
            "variants": [
                ("5mg", Decimal("60.00")),
            ],
        },
        {
            "name": "10ml BAC Water 0.9% Benz",
            "description": (
                "Bacteriostatic water (0.9% benzyl alcohol) for reconstitution "
                "of research peptides in laboratory settings."
            ),
            "is_accessory": True,
            "variants": [
                ("10ml", Decimal("5.00")),
            ],
        },
        {
            "name": "Pack of 10 Needles (29G x 12.7mm)",
            "description": (
                "Sterile injection needles suitable for precise laboratory "
                "peptide handling and administration in controlled research "
                "environments."
            ),
            "is_accessory": True,
            "variants": [
                ("Pack of 10", Decimal("5.00")),
            ],
        },
    ]

    for item in products:
        product = Product.objects.filter(name__iexact=item["name"]).first()
        base_price = min(price for _, price in item["variants"])

        if not product:
            product = Product.objects.create(
                name=item["name"],
                description=item["description"],
                price=base_price,
                is_active=True,
                is_accessory=item["is_accessory"],
            )
        else:
            update_fields = []
            if product.description != item["description"]:
                product.description = item["description"]
                update_fields.append("description")
            if product.price != base_price:
                product.price = base_price
                update_fields.append("price")
            if not product.is_active:
                product.is_active = True
                update_fields.append("is_active")
            if product.is_accessory != item["is_accessory"]:
                product.is_accessory = item["is_accessory"]
                update_fields.append("is_accessory")
            if update_fields:
                product.save(update_fields=update_fields)

        for strength, price in item["variants"]:
            variant, _ = ProductVariant.objects.get_or_create(
                product=product,
                strength=strength,
                defaults={
                    "price": price,
                    "is_active": True,
                },
            )

            variant_updates = []
            if variant.price != price:
                variant.price = price
                variant_updates.append("price")
            if not variant.is_active:
                variant.is_active = True
                variant_updates.append("is_active")
            if variant_updates:
                variant.save(update_fields=variant_updates)


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0007_product_is_accessory_and_seed_accessories"),
    ]

    operations = [
        migrations.RunPython(seed_client_products, migrations.RunPython.noop),
    ]
