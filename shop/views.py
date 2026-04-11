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

# Full shop page view.
def shop(request):
    products = Product.objects.filter(is_active=True)
    return render(
        request,
        "shop.html",
        {
            "products": products,
        },
    )


def certificates(request):
    return render(request, "certificates.html")




def about(request):
    return render(request, "about.html")



def faq(request):
    return render(request, "faq.html")




def contact(request):
    return render(request, "contact.html")

