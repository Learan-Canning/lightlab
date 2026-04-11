from django.shortcuts import render
from .models import Product


# Homepage view: loads products and renders the one-page storefront.
def home(request):
    all_products = Product.objects.filter(is_active=True)
    products = all_products[:6]
    total_products = all_products.count()

    return render(
        request,
        "home.html",
        {
            "products": products,
            "total_products": total_products,
        },
    )
