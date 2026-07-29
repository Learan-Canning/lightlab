from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem, ProductVariant, _generate_reference
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Case, IntegerField, Value, When, F
from django.http import HttpResponseForbidden


PINNED_ACCESSORY_NAMES = [
    "10ml BAC Water 0.9% Benz",
    "10ml Bacteriostatic Water (Non-Alcohol)",
]


def _is_stock_tracked(variant):
    return variant.qty_in_stock is not None


def _is_variant_in_stock(variant):
    if not _is_stock_tracked(variant):
        return True
    return variant.qty_in_stock > 0


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
    core_products = products.filter(is_accessory=False).order_by("name")
    accessory_products = (
        products.filter(is_accessory=True)
        .annotate(
            display_priority=Case(
                When(name__iexact=PINNED_ACCESSORY_NAMES[0], then=Value(0)),
                When(name__iexact=PINNED_ACCESSORY_NAMES[1], then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        )
        .order_by("display_priority", "name")
    )

    return render(
        request,
        "shop.html",
        {
            "products": products,
            "total_products": products.count(),
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
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            quantity = 1

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

        if not _is_variant_in_stock(variant):
            messages.error(request, "That bottle option is currently out of stock.")
            return redirect(request.POST.get("next", "shop"))

        if "cart" not in request.session:
            request.session["cart"] = {}

        cart = request.session["cart"]
        cart_key = str(variant.id)

        requested_quantity = quantity + int(cart.get(cart_key, 0))
        if _is_stock_tracked(variant) and requested_quantity > variant.qty_in_stock:
            messages.error(request, f"Only {variant.qty_in_stock} available for {variant.product.name} {variant.strength}.")
            return redirect(request.POST.get("next", "shop"))

        cart[cart_key] = requested_quantity

        request.session.modified = True
        messages.success(request, f"{variant.product.name} {variant.strength} added to cart!")
        return redirect(request.POST.get("next", "shop"))

    return redirect("shop")


def cart(request):
    cart_data = request.session.get("cart", {})
    cart_items = []
    subtotal = Decimal("0.00")

    for variant_id, quantity in list(cart_data.items()):
        try:
            variant = ProductVariant.objects.select_related("product").get(
                id=int(variant_id),
                is_active=True,
                product__is_active=True,
            )

            if not _is_variant_in_stock(variant):
                del cart_data[variant_id]
                continue

            if _is_stock_tracked(variant) and quantity > variant.qty_in_stock:
                quantity = variant.qty_in_stock
                if quantity < 1:
                    del cart_data[variant_id]
                    continue
                cart_data[variant_id] = quantity
                messages.info(request, f"Updated {variant.product.name} {variant.strength} to available stock ({quantity}).")

            item_total = Decimal(variant.price) * Decimal(quantity)
            subtotal += item_total

            cart_items.append({
                "variant": variant,
                "product": variant.product,
                "quantity": quantity,
                "item_total": item_total,
            })
        except ProductVariant.DoesNotExist:
            del cart_data[variant_id]

    tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    total = (subtotal + tax).quantize(Decimal("0.01"))

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

                subtotal = Decimal("0.00")
                created_items = 0

                for variant_id, qty in cart.items():
                    try:
                        variant = ProductVariant.objects.select_for_update().select_related("product").get(
                            pk=int(variant_id),
                            is_active=True,
                            product__is_active=True,
                        )
                    except ProductVariant.DoesNotExist:
                        raise ValueError("One or more cart items are no longer available. Please review your cart.")

                    try:
                        quantity = int(qty)
                    except (TypeError, ValueError):
                        quantity = 1

                    if quantity < 1:
                        raise ValueError("One or more cart quantities are invalid. Please review your cart.")

                    if _is_stock_tracked(variant):
                        if variant.qty_in_stock < 1:
                            raise ValueError(f"{variant.product.name} {variant.strength} is out of stock.")
                        if quantity > variant.qty_in_stock:
                            raise ValueError(
                                f"Only {variant.qty_in_stock} available for {variant.product.name} {variant.strength}."
                            )

                    unit_price = variant.price
                    line_total = Decimal(unit_price) * Decimal(quantity)
                    subtotal += line_total
                    created_items += 1

                    OrderItem.objects.create(
                        order=order,
                        product=variant.product,
                        variant=variant,
                        unit_price=unit_price,
                        quantity=quantity,
                        line_total=line_total,
                    )

                    if _is_stock_tracked(variant):
                        ProductVariant.objects.filter(pk=variant.pk).update(
                            qty_in_stock=F("qty_in_stock") - quantity
                        )

                if created_items == 0:
                    raise ValueError("No valid items were found in your cart.")

                tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
                total = (subtotal + tax).quantize(Decimal("0.01"))
                order.total_amount = total
                order.save(update_fields=["total_amount"])

            break
        except IntegrityError:
            order = None
            if attempt == 4:
                messages.error(request, "Could not create order. Please try again.")
                return redirect("cart")
        except ValueError as exc:
            messages.error(request, str(exc))
            return redirect("cart")

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
            try:
                variant = ProductVariant.objects.get(pk=int(variant_id), is_active=True, product__is_active=True)
            except ProductVariant.DoesNotExist:
                del cart_data[variant_id]
                request.session["cart"] = cart_data
                request.session.modified = True
                messages.error(request, "That item is no longer available.")
                return redirect("cart")

            if _is_stock_tracked(variant):
                if variant.qty_in_stock < 1:
                    del cart_data[variant_id]
                    request.session["cart"] = cart_data
                    request.session.modified = True
                    messages.error(request, f"{variant.product.name} {variant.strength} is out of stock.")
                    return redirect("cart")

                if quantity > variant.qty_in_stock:
                    quantity = variant.qty_in_stock
                    messages.info(request, f"Quantity adjusted to available stock ({quantity}).")

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


def manager_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("manager_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Invalid username or password.")
            return redirect("manager_login")

        if not user.is_staff:
            messages.error(request, "This account does not have manager access.")
            return redirect("manager_login")

        login(request, user)
        messages.success(request, "Welcome back.")
        return redirect("manager_dashboard")

    return render(request, "manager_login.html")


@login_required
def manager_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("manager_login")


@login_required
def manager_dashboard(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Manager access only.")

    valid_statuses = {choice[0] for choice in Order.STATUS_CHOICES}

    def _parse_price(raw_value):
        value = (raw_value or "").strip()
        if not value:
            raise ValueError("Price is required.")
        price = Decimal(value)
        if price < 0:
            raise ValueError("Price cannot be negative.")
        return price

    def _parse_optional_stock(raw_value):
        value = (raw_value or "").strip()
        if value == "":
            return None
        qty = int(value)
        if qty < 0:
            raise ValueError("Stock cannot be negative.")
        return qty

    if request.method == "POST":
        action = request.POST.get("action", "").strip()

        if action == "update_stock":
            try:
                variant_id = int(request.POST.get("variant_id", ""))
                qty_in_stock = int(request.POST.get("qty_in_stock", ""))
            except (TypeError, ValueError):
                messages.error(request, "Please enter a valid stock number.")
                return redirect("manager_dashboard")

            if qty_in_stock < 0:
                messages.error(request, "Stock cannot be negative.")
                return redirect("manager_dashboard")

            variant = ProductVariant.objects.select_related("product").filter(pk=variant_id).first()
            if not variant:
                messages.error(request, "Variant not found.")
                return redirect("manager_dashboard")

            variant.qty_in_stock = qty_in_stock
            variant.save(update_fields=["qty_in_stock"])
            messages.success(request, f"Updated stock for {variant.product.name} {variant.strength}.")
            return redirect("manager_dashboard")

        if action == "update_order_status":
            try:
                order_id = int(request.POST.get("order_id", ""))
            except (TypeError, ValueError):
                messages.error(request, "Order selection is invalid.")
                return redirect("manager_dashboard")

            new_status = request.POST.get("status", "").strip().lower()
            if new_status not in valid_statuses:
                messages.error(request, "Order status is invalid.")
                return redirect("manager_dashboard")

            order = Order.objects.filter(pk=order_id).first()
            if not order:
                messages.error(request, "Order not found.")
                return redirect("manager_dashboard")

            order.status = new_status
            order.save(update_fields=["status"])
            messages.success(
                request,
                f"Order {order.reference} marked as {order.get_status_display()}.",
            )
            return redirect("manager_dashboard")

        if action == "create_product":
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()
            image = request.FILES.get("image")

            if not name:
                messages.error(request, "Product name is required.")
                return redirect("manager_dashboard")

            try:
                price = _parse_price(request.POST.get("price", ""))
            except (ArithmeticError, ValueError):
                messages.error(request, "Please enter a valid product price.")
                return redirect("manager_dashboard")

            product = Product.objects.create(
                name=name,
                price=price,
                description=description,
                is_active=(request.POST.get("is_active") == "on"),
                is_accessory=(request.POST.get("is_accessory") == "on"),
                image=image,
            )
            messages.success(request, f"Created product {product.name}.")
            return redirect("manager_dashboard")

        if action == "update_product":
            try:
                product_id = int(request.POST.get("product_id", ""))
            except (TypeError, ValueError):
                messages.error(request, "Product selection is invalid.")
                return redirect("manager_dashboard")

            product = Product.objects.filter(pk=product_id).first()
            if not product:
                messages.error(request, "Product not found.")
                return redirect("manager_dashboard")

            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()
            image = request.FILES.get("image")

            if not name:
                messages.error(request, "Product name is required.")
                return redirect("manager_dashboard")

            try:
                price = _parse_price(request.POST.get("price", ""))
            except (ArithmeticError, ValueError):
                messages.error(request, "Please enter a valid product price.")
                return redirect("manager_dashboard")

            product.name = name
            product.price = price
            product.description = description
            product.is_active = request.POST.get("is_active") == "on"
            product.is_accessory = request.POST.get("is_accessory") == "on"

            if request.POST.get("clear_image") == "1":
                product.image = None
            if image:
                product.image = image

            product.save()
            messages.success(request, f"Updated product {product.name}.")
            return redirect("manager_dashboard")

        if action == "delete_product":
            try:
                product_id = int(request.POST.get("product_id", ""))
            except (TypeError, ValueError):
                messages.error(request, "Product selection is invalid.")
                return redirect("manager_dashboard")

            product = Product.objects.filter(pk=product_id).first()
            if not product:
                messages.error(request, "Product not found.")
                return redirect("manager_dashboard")

            product_name = product.name
            product.delete()
            messages.success(request, f"Deleted product {product_name}.")
            return redirect("manager_dashboard")

        if action == "create_variant":
            try:
                product_id = int(request.POST.get("product_id", ""))
            except (TypeError, ValueError):
                messages.error(request, "Product selection is invalid.")
                return redirect("manager_dashboard")

            product = Product.objects.filter(pk=product_id).first()
            if not product:
                messages.error(request, "Product not found.")
                return redirect("manager_dashboard")

            strength = request.POST.get("strength", "").strip()
            if not strength:
                messages.error(request, "Variant strength is required.")
                return redirect("manager_dashboard")

            try:
                price = _parse_price(request.POST.get("price", ""))
                qty_in_stock = _parse_optional_stock(request.POST.get("qty_in_stock", ""))
            except (ArithmeticError, TypeError, ValueError):
                messages.error(request, "Please enter valid variant price and stock values.")
                return redirect("manager_dashboard")

            try:
                ProductVariant.objects.create(
                    product=product,
                    strength=strength,
                    price=price,
                    is_active=(request.POST.get("is_active") == "on"),
                    qty_in_stock=qty_in_stock,
                )
            except IntegrityError:
                messages.error(request, "That variant strength already exists for this product.")
                return redirect("manager_dashboard")

            messages.success(request, f"Created variant {product.name} {strength}.")
            return redirect("manager_dashboard")

        if action == "update_variant":
            try:
                variant_id = int(request.POST.get("variant_id", ""))
            except (TypeError, ValueError):
                messages.error(request, "Variant selection is invalid.")
                return redirect("manager_dashboard")

            variant = ProductVariant.objects.select_related("product").filter(pk=variant_id).first()
            if not variant:
                messages.error(request, "Variant not found.")
                return redirect("manager_dashboard")

            strength = request.POST.get("strength", "").strip()
            if not strength:
                messages.error(request, "Variant strength is required.")
                return redirect("manager_dashboard")

            try:
                price = _parse_price(request.POST.get("price", ""))
                qty_in_stock = _parse_optional_stock(request.POST.get("qty_in_stock", ""))
            except (ArithmeticError, TypeError, ValueError):
                messages.error(request, "Please enter valid variant price and stock values.")
                return redirect("manager_dashboard")

            variant.strength = strength
            variant.price = price
            variant.qty_in_stock = qty_in_stock
            variant.is_active = request.POST.get("is_active") == "on"

            try:
                variant.save()
            except IntegrityError:
                messages.error(request, "That variant strength already exists for this product.")
                return redirect("manager_dashboard")

            messages.success(
                request,
                f"Updated variant {variant.product.name} {variant.strength}.",
            )
            return redirect("manager_dashboard")

        if action == "delete_variant":
            try:
                variant_id = int(request.POST.get("variant_id", ""))
            except (TypeError, ValueError):
                messages.error(request, "Variant selection is invalid.")
                return redirect("manager_dashboard")

            variant = ProductVariant.objects.select_related("product").filter(pk=variant_id).first()
            if not variant:
                messages.error(request, "Variant not found.")
                return redirect("manager_dashboard")

            variant_name = f"{variant.product.name} {variant.strength}"
            variant.delete()
            messages.success(request, f"Deleted variant {variant_name}.")
            return redirect("manager_dashboard")

    tracked_variants = (
        ProductVariant.objects.select_related("product")
        .filter(product__is_active=True, is_active=True, qty_in_stock__isnull=False)
        .order_by("qty_in_stock", "product__name", "strength")
    )

    low_stock_variants = tracked_variants.filter(qty_in_stock__gt=0, qty_in_stock__lte=3)
    out_of_stock_variants = tracked_variants.filter(qty_in_stock=0)
    recent_orders = (
        Order.objects.prefetch_related("items__product", "items__variant")
        .order_by("-created_at")[:100]
    )
    paid_order_count = Order.objects.filter(status=Order.STATUS_PAID).count()
    cancelled_order_count = Order.objects.filter(status=Order.STATUS_CANCELLED).count()
    manager_products = (
        Product.objects.prefetch_related("variants")
        .order_by("name")[:100]
    )

    context = {
        "product_count": Product.objects.filter(is_active=True).count(),
        "tracked_variant_count": tracked_variants.count(),
        "low_stock_count": low_stock_variants.count(),
        "out_of_stock_count": out_of_stock_variants.count(),
        "pending_order_count": Order.objects.filter(status=Order.STATUS_PENDING).count(),
        "paid_order_count": paid_order_count,
        "cancelled_order_count": cancelled_order_count,
        "low_stock_variants": low_stock_variants,
        "out_of_stock_variants": out_of_stock_variants,
        "tracked_variants": tracked_variants[:100],
        "recent_orders": recent_orders,
        "order_status_choices": Order.STATUS_CHOICES,
        "manager_products": manager_products,
    }
    return render(request, "manager_dashboard.html", context)





