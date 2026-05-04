from django.urls import path, include
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
    path("comptabilite/", views.ComptabiliteView.as_view(), name="comptabilite"),
    path("comptabilite/<int:pk>/supprimer/", views.TransactionDeleteView.as_view(), name="transaction_delete"),
    path("historiques/", views.HistoriquesView.as_view(), name="historiques"),
    path("historiques/<int:pk>/detail/", views.LogDetailView.as_view(), name="log_detail"),
    path("", include("apps.stock.urls")),
]
