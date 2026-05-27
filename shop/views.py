from django.shortcuts import render, redirect
from .models import Product, Order, OrderItem, _generate_reference
from django.core.mail import send_mail
from django.contrib import messages
from decimal import Decimal
from django.conf import settings
from django.db import transaction, IntegrityError


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
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Validation
        if not all([name, email, subject, message]):
            messages.error(request, 'Please fill in all fields.')
            return redirect('contact')

        # Send email
        try:
            send_mail(
                subject=f'New Contact Form: {subject}',
                message=f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
                from_email=email,
                recipient_list=['hello@lightlab.com'],
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('contact')

    return render(request, 'contact.html')

def add_to_cart(request):
    """
    Handles adding a product to the session-based cart.
    Called when customer clicks 'Add to Cart' button.
    """
    if request.method == 'POST':
         # Get the product ID from the form
        product_id = request.POST.get('product_id')
        # Get quantity (default to 1 if not provided)
        quantity = int(request.POST.get('quantity', 1))
        
        # Initialize cart in session if it doesn't exist yet
        # Cart format: {'product_id': quantity, 'product_id': quantity, ...}
        if 'cart' not in request.session:
            request.session['cart'] = {}
        
        cart = request.session['cart']
        
        # If product already in cart, add to quantity. Otherwise, add it.
        if str(product_id) in cart:
            cart[str(product_id)] += quantity
        else:
            cart[str(product_id)] = quantity
        
        # Save the session (required for changes to take effect)
        request.session.modified = True
        
        # Show success message to user
        messages.success(request, 'Product added to cart!')
        
        # Redirect back to where they came from (shop or home)
        return redirect(request.POST.get('next', 'shop'))
    
    # If not POST request, redirect to shop
    return redirect('shop')

def cart(request):
    """
    Display the shopping cart page.
    Shows all items in session cart with prices, quantities, and totals.
    """
    # Get cart from session (empty dict if no cart yet)
    cart_data = request.session.get('cart', {})
    
    # Fetch product details for items in cart
    cart_items = []
    subtotal = 0
    
    for product_id, quantity in cart_data.items():
        try:
            product = Product.objects.get(id=int(product_id))
            item_total = float(product.price) * quantity
            subtotal += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            # Remove product if it no longer exists
            del cart_data[product_id]
    
    # Calculate tax (10%) and total
    tax = subtotal * 0.10
    total = subtotal + tax
    
    # Save session if we removed any deleted products
    request.session.modified = True
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'cart_count': len(cart_items),
    })


def create_order(request):
    if request.method != "POST":
        return redirect("cart")

    email = request.POST.get("email", "").strip()
    name = request.POST.get("name", "").strip()
    if not email:
        messages.error(request, "Email is required to complete checkout.")
        return redirect("cart")

    cart = request.session.get("cart", {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    # Create order with retry to avoid rare reference collisions
    order = None
    for attempt in range(5):
        reference = _generate_reference()
        try:
            with transaction.atomic():
                order = Order.objects.create(reference=reference, email=email, name=name)
            break
        except IntegrityError:
            order = None
            if attempt == 4:
                messages.error(request, "Could not create order. Please try again.")
                return redirect("cart")

    # Build items and totals
    subtotal = Decimal("0.00")
    for pid, qty in cart.items():
        try:
            product = Product.objects.get(pk=int(pid), is_active=True)
        except Product.DoesNotExist:
            continue
        unit_price = product.price
        quantity = int(qty)
        line_total = Decimal(unit_price) * quantity
        subtotal += line_total
        OrderItem.objects.create(
            order=order,
            product=product,
            unit_price=unit_price,
            quantity=quantity,
            line_total=line_total,
        )

    tax = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"))
    total = (subtotal + tax).quantize(Decimal("0.01"))
    order.total_amount = total
    order.save()

    # Clear cart
    request.session['cart'] = {}
    request.session.modified = True

    # Send confirmation email with bank details and strict reference line
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
    bank_lines = [
        f"Account name: {settings.BANK_ACCOUNT_NAME}",
        f"Account number: {settings.BANK_ACCOUNT_NUMBER}",
        f"Sort code: {settings.BANK_SORT_CODE}",
    ]
    bank_text = "\n".join(bank_lines)
    payment_reference_line = f"PAY USING REFERENCE: {order.reference}"

    subject = f"LightLab order {order.reference} — Payment instructions"
    message = (
        f"Thank you for your order.\n\n"
        f"Amount to pay: £{order.total_amount}\n\n"
        f"{bank_text}\n\n"
        f"{payment_reference_line}\n\n"
        "Please use the reference above when making the bank transfer."
    )
    send_mail(subject, message, from_email, [order.email], fail_silently=False)

    return redirect("order_confirmation", reference=order.reference)


def order_confirmation(request, reference):
    try:
        order = Order.objects.get(reference=reference)
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
    return redirect('cart')

def update_cart(request):
    if request.method == 'POST':
        product_id = str(request.POST.get('product_id', ''))
        quantity_raw = request.POST.get('quantity', '1')

        try:
            quantity = int(quantity_raw)
        except ValueError:
            quantity = 1

        if quantity < 1:
            quantity = 1

        cart_data = request.session.get('cart', {})

        if product_id in cart_data:
            cart_data[product_id] = quantity
            request.session['cart'] = cart_data
            request.session.modified = True
            messages.success(request, 'Cart quantity updated.')

    return redirect('cart')


def remove_from_cart(request):
    if request.method == 'POST':
        product_id = str(request.POST.get('product_id', ''))
        cart_data = request.session.get('cart', {})

        if product_id in cart_data:
            del cart_data[product_id]
            request.session['cart'] = cart_data
            request.session.modified = True
            messages.success(request, 'Item removed from cart.')

    return redirect('cart')



