from django.urls import path
from . import views


# App-level URL routes for the shop app.
urlpatterns = [
    # Site root points to the homepage view.
    path("", views.home, name="home"),
]