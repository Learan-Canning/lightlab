from django.urls import path
from . import views


# App-level URL routes for the shop app.
urlpatterns = [
    # Site root points to the homepage view.
    path("", views.home, name="home"),

    # Main shop page route.
    path("shop/", views.shop, name="shop"),

    # Static content pages.
    path("certificates/", views.certificates, name="certificates"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("contact/", views.contact, name="contact"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.cart, name="cart"),
    path("cart/update/", views.update_cart, name="update_cart"),
    path("cart/remove/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/create/", views.create_order, name="create_order"),
    path(
        "checkout/<str:reference>/",
        views.order_confirmation,
        name="order_confirmation",
    ),
    path("checkout/cancel/", views.checkout_cancel, name="checkout_cancel"),

    # Lightweight manager portal routes for client-friendly inventory workflow.
    path("manager/login/", views.manager_login, name="manager_login"),
    path("manager/logout/", views.manager_logout, name="manager_logout"),
    path(
        "manager/dashboard/",
        views.manager_dashboard,
        name="manager_dashboard",
    ),
]
