from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Count, F
from django.utils import timezone
from datetime import timedelta

from apps.stock.models import Product, Category, StockMovement, Cart, Order
from apps.website.models import ContactMessage


class DashboardHomeView(LoginRequiredMixin, View):
    def get(self, request):
        today = timezone.now()
        last_30_days = today - timedelta(days=30)

        total_products = Product.objects.filter(is_active=True).count()
        low_stock_products = Product.objects.filter(
            is_active=True,
            quantity_in_stock__lte=F("min_stock_level")
        ).count()
        out_of_stock = Product.objects.filter(is_active=True, quantity_in_stock=0).count()

        total_stock_value = sum(
            p.stock_value for p in Product.objects.filter(is_active=True)
        )

        recent_movements = StockMovement.objects.select_related("product", "created_by").order_by("-created_at")[:10]
        categories = Category.objects.annotate(prod_count=Count("products")).all()

        new_messages = ContactMessage.objects.filter(status="new").count()

        movements_in = StockMovement.objects.filter(
            movement_type="in", created_at__gte=last_30_days
        ).count()
        movements_out = StockMovement.objects.filter(
            movement_type="out", created_at__gte=last_30_days
        ).count()

        cart_total = 0
        cart_items_count = 0
        try:
            cart = request.user.cart
            cart_total = cart.total_price
            cart_items_count = cart.total_items
        except Cart.DoesNotExist:
            pass

        low_stock_list = Product.objects.filter(
            is_active=True, quantity_in_stock__lte=F("min_stock_level")
        ).select_related("category")[:8]

        chart_categories = list(categories.values_list("name", flat=True))
        chart_values = [c.prod_count for c in categories]

        context = {
            "total_products": total_products,
            "low_stock_products": low_stock_products,
            "out_of_stock": out_of_stock,
            "total_stock_value": total_stock_value,
            "recent_movements": recent_movements,
            "categories": categories,
            "new_messages": new_messages,
            "movements_in": movements_in,
            "movements_out": movements_out,
            "cart_total": cart_total,
            "cart_items_count": cart_items_count,
            "low_stock_list": low_stock_list,
            "chart_categories": chart_categories,
            "chart_values": chart_values,
        }
        return render(request, "stock/dashboard_home.html", context)
