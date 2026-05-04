from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("services/", views.ServicesPageView.as_view(), name="services"),
    path("projets/", views.ProjetsPageView.as_view(), name="projets"),
    path("equipe/", views.EquipePageView.as_view(), name="equipe"),
    path("contact/", views.ContactView.as_view(), name="contact"),
]
