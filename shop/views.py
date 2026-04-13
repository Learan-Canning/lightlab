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


# certificates view example
def certificates(request):
    certificates = [
        {
            "title": "Retatrutide 10mg Certificate of Analysis",
            "product": "Retatrutide 10mg",
            "batch": "RET-2026-001",
            "purity": 99.1,
            "tested": "Mar 1, 2026",
        },
        {
            "title": "Retatrutide 20mg Certificate of Analysis",
            "product": "Retatrutide 20mg",
            "batch": "RET-2026-002",
            "purity": 98.9,
            "tested": "Mar 1, 2026",
        },
        {
            "title": "Retatrutide 30mg Certificate of Analysis",
            "product": "Retatrutide 30mg",
            "batch": "RET-2026-003",
            "purity": 99.0,
            "tested": "Mar 1, 2026",
        },
        {
            "title": "Tirzepatide 10mg Certificate of Analysis",
            "product": "Tirzepatide 10mg",
            "batch": "TIR-2026-001",
            "purity": 98.8,
            "tested": "Mar 5, 2026",
        },
        {
            "title": "Tirzepatide 20mg Certificate of Analysis",
            "product": "Tirzepatide 20mg",
            "batch": "TIR-2026-002",
            "purity": 99.2,
            "tested": "Mar 5, 2026",
        },
        {
            "title": "BPC-157 5mg Certificate of Analysis",
            "product": "BPC-157 5mg",
            "batch": "BPC-2026-001",
            "purity": 99.2,
            "tested": "Feb 15, 2026",
        },
        {
            "title": "TB-500 5mg Certificate of Analysis",
            "product": "TB-500 5mg",
            "batch": "TB5-2026-001",
            "purity": 98.7,
            "tested": "Feb 20, 2026",
        },
        {
            "title": "GHK-Cu 50mg Certificate of Analysis",
            "product": "GHK-Cu 50mg",
            "batch": "GHK-2026-001",
            "purity": 98.6,
            "tested": "Feb 28, 2026",
        },
    ]

    return render(request, "certificates.html", {"certificates": certificates})


def about(request):
    return render(request, "about.html")



def faq(request):
    return render(request, "faq.html")




def contact(request):
    return render(request, "contact.html")

