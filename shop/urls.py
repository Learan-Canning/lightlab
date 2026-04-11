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
]