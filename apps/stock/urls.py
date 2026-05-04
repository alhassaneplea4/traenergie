from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.ProductListView.as_view(), name="products"),
    path("products/create/", views.ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("movements/", views.StockMovementView.as_view(), name="stock_movements"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
    path("cart/update/<int:item_id>/", views.cart_update_qty, name="cart_update"),
    path("cart/checkout/", views.cart_checkout, name="cart_checkout"),
]
