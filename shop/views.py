from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem, ProductVariant, _generate_reference
from django.core.mail import send_mail
from django.contrib import messages
from decimal import Decimal
from django.conf import settings
from django.db import IntegrityError, transaction


RESEARCH_SUPPLY_BUNDLE_NAME = "Research Supply Bundle"


# Homepage view: loads products and renders the one-page storefront.
def home(request):
    all_products = Product.objects.filter(is_active=True)
    products = all_products.prefetch_related("variants")[:6]
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
    products = Product.objects.filter(is_active=True).prefetch_related("variants")
    featured_bundle = products.filter(name__iexact=RESEARCH_SUPPLY_BUNDLE_NAME).first()
    featured_bundle_variant = None
    if featured_bundle:
        featured_bundle_variant = (
            featured_bundle.variants.filter(is_active=True).order_by("price", "id").first()
        )

    core_products = products.filter(is_accessory=False)
    accessory_products = products.filter(is_accessory=True)

    if featured_bundle:
        core_products = core_products.exclude(pk=featured_bundle.pk)
        accessory_products = accessory_products.exclude(pk=featured_bundle.pk)

    return render(
        request,
        "shop.html",
        {
            "products": products,
            "total_products": products.count(),
            "featured_bundle": featured_bundle,
            "featured_bundle_variant": featured_bundle_variant,
            "core_products": core_products,
            "accessory_products": accessory_products,
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
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        if not all([name, email, subject, message]):
            messages.error(request, "Please fill in all fields.")
            return redirect("contact")

        try:
            send_mail(
                subject=f"New Contact Form: {subject}",
                message=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_FORM_TO_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect("contact")
        except Exception:
            messages.error(request, "An error occurred. Please try again.")
            return redirect("contact")

    return render(request, "contact.html")


def add_to_cart(request):
    if request.method == "POST":
        variant_id = request.POST.get("variant_id")
        quantity = int(request.POST.get("quantity", 1))

        if not variant_id:
            messages.error(request, "Please choose a bottle strength.")
            return redirect(request.POST.get("next", "shop"))

        try:
            variant = ProductVariant.objects.select_related("product").get(
                id=int(variant_id),
                is_active=True,
                product__is_active=True,
            )
        except ProductVariant.DoesNotExist:
            messages.error(request, "That bottle option is no longer available.")
            return redirect(request.POST.get("next", "shop"))

        if "cart" not in request.session:
            request.session["cart"] = {}

        cart = request.session["cart"]
        cart_key = str(variant.id)

        if cart_key in cart:
            cart[cart_key] += quantity
        else:
            cart[cart_key] = quantity

        request.session.modified = True
        messages.success(request, f"{variant.product.name} {variant.strength} added to cart!")
        return redirect(request.POST.get("next", "shop"))

    return redirect("shop")


def cart(request):
    cart_data = request.session.get("cart", {})
    cart_items = []
    subtotal = 0

    for variant_id, quantity in list(cart_data.items()):
        try:
            variant = ProductVariant.objects.select_related("product").get(id=int(variant_id))
            item_total = float(variant.price) * quantity
            subtotal += item_total

            cart_items.append({
                "variant": variant,
                "product": variant.product,
                "quantity": quantity,
                "item_total": item_total,
            })
        except ProductVariant.DoesNotExist:
            del cart_data[variant_id]

    tax = subtotal * 0.10
    total = subtotal + tax

    request.session["cart"] = cart_data
    request.session.modified = True

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax": tax,
        "total": total,
        "cart_count": len(cart_items),
    })


def create_order(request):
    if request.method != "POST":
        return redirect("cart")

    email = request.POST.get("email", "").strip()
    name = request.POST.get("name", "").strip()
    address_line_1 = request.POST.get("address_line_1", "").strip()
    address_line_2 = request.POST.get("address_line_2", "").strip()
    town_or_city = request.POST.get("town_or_city", "").strip()
    county = request.POST.get("county", "").strip()
    postcode = request.POST.get("postcode", "").strip()
    country = request.POST.get("country", "United Kingdom").strip()

    if not email:
        messages.error(request, "Email is required to complete checkout.")
        return redirect("cart")
    if not address_line_1 or not town_or_city or not postcode:
        messages.error(request, "Please provide a full postal address (street, town/city and postcode).")
        return redirect("cart")

    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    order = None
    for attempt in range(5):
        reference = _generate_reference()
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    reference=reference,
                    email=email,
                    name=name,
                    address_line_1=address_line_1,
                    address_line_2=address_line_2,
                    town_or_city=town_or_city,
                    county=county,
                    postcode=postcode,
                    country=country,
                )
            break
        except IntegrityError:
            order = None
            if attempt == 4:
                messages.error(request, "Could not create order. Please try again.")
                return redirect("cart")

    subtotal = Decimal("0.00")
    for variant_id, qty in cart.items():
        try:
            variant = ProductVariant.objects.select_related("product").get(
                pk=int(variant_id),
                is_active=True,
                product__is_active=True,
            )
        except ProductVariant.DoesNotExist:
            continue

        unit_price = variant.price
        quantity = int(qty)
        line_total = Decimal(unit_price) * quantity
        subtotal += line_total

        OrderItem.objects.create(
            order=order,
            product=variant.product,
            variant=variant,
            unit_price=unit_price,
            quantity=quantity,
            line_total=line_total,
        )

    include_bundle = request.POST.get("include_research_bundle") in {"1", "true", "True", "on"}
    if include_bundle:
        bundle_variant = (
            ProductVariant.objects.select_related("product")
            .filter(
                product__name__iexact=RESEARCH_SUPPLY_BUNDLE_NAME,
                product__is_active=True,
                is_active=True,
            )
            .order_by("price", "id")
            .first()
        )
        if bundle_variant:
            bundle_line_total = Decimal(bundle_variant.price)
            subtotal += bundle_line_total
            OrderItem.objects.create(
                order=order,
                product=bundle_variant.product,
                variant=bundle_variant,
                unit_price=bundle_variant.price,
                quantity=1,
                line_total=bundle_line_total,
            )

    tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    total = (subtotal + tax).quantize(Decimal("0.01"))
    order.total_amount = total
    order.save()

    request.session["cart"] = {}
    request.session.modified = True

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    bank_lines = [
        f"Account name: {settings.BANK_ACCOUNT_NAME}",
        f"Account number: {settings.BANK_ACCOUNT_NUMBER}",
        f"Sort code: {settings.BANK_SORT_CODE}",
    ]
    bank_text = "\n".join(bank_lines)
    payment_reference_line = f"PAY USING REFERENCE: {order.reference}"

    subject = f"LightLab order {order.reference} - Payment instructions"
    customer_message = (
        f"Thank you for your order.\n\n"
        f"Amount to pay: £{order.total_amount}\n\n"
        f"{bank_text}\n\n"
        f"{payment_reference_line}\n\n"
        "Please use the reference above when making the bank transfer."
    )

    send_mail(subject, customer_message, from_email, [order.email], fail_silently=False)

    order_lines = []
    for item in order.items.select_related("product", "variant").all():
        variant_label = item.variant.strength if item.variant else "legacy item"
        order_lines.append(
            f"- {item.product.name} {variant_label} x{item.quantity} @ £{item.unit_price} = £{item.line_total}"
        )
    order_items_text = "\n".join(order_lines) if order_lines else "- No items"

    internal_subject = f"NEW ORDER {order.reference} - Dispatch details"
    internal_message = (
        f"Reference: {order.reference}\n"
        f"Created: {order.created_at}\n\n"
        f"Customer email: {order.email}\n"
        f"Customer name: {order.name or '(not provided)'}\n\n"
        f"Shipping address:\n"
        f"{order.address_line_1}\n"
        f"{order.address_line_2}\n"
        f"{order.town_or_city}\n"
        f"{order.county}\n"
        f"{order.postcode}\n"
        f"{order.country}\n\n"
        f"Order items:\n{order_items_text}\n\n"
        f"Subtotal + tax total: £{order.total_amount}\n"
        f"Payment reference required: {order.reference}\n"
    )

    send_mail(
        internal_subject,
        internal_message,
        from_email,
        [settings.CONTACT_FORM_TO_EMAIL],
        fail_silently=False,
    )

    return redirect("order_confirmation", reference=order.reference)


def order_confirmation(request, reference):
    try:
        order = Order.objects.prefetch_related("items__variant").get(reference=reference)
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("shop")

    bank = {
        "name": settings.BANK_ACCOUNT_NAME,
        "number": settings.BANK_ACCOUNT_NUMBER,
        "sort_code": settings.BANK_SORT_CODE,
    }
    return render(request, "order_confirmation.html", {"order": order, "bank": bank})


def checkout_cancel(request):
    messages.info(request, "Checkout cancelled.")
    return redirect("cart")


def update_cart(request):
    if request.method == "POST":
        variant_id = str(request.POST.get("variant_id", ""))
        quantity_raw = request.POST.get("quantity", "1")

        try:
            quantity = int(quantity_raw)
        except ValueError:
            quantity = 1

        if quantity < 1:
            quantity = 1

        cart_data = request.session.get("cart", {})

        if variant_id in cart_data:
            cart_data[variant_id] = quantity
            request.session["cart"] = cart_data
            request.session.modified = True
            messages.success(request, "Cart quantity updated.")

    return redirect("cart")


def remove_from_cart(request):
    if request.method == "POST":
        variant_id = str(request.POST.get("variant_id", ""))
        cart_data = request.session.get("cart", {})

        if variant_id in cart_data:
            del cart_data[variant_id]
            request.session["cart"] = cart_data
            request.session.modified = True
            messages.success(request, "Item removed from cart.")

    return redirect("cart")



