from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("services/", views.ServicesPageView.as_view(), name="services"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
