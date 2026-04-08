from django.shortcuts import render
from .models import Product


# Homepage view: loads products and renders the one-page storefront.
def home(request):
    # Pull all products for the shop grid.
    products = Product.objects.all()

    # Send products into the template context.
    return render(request, "home.html", {"products": products})
