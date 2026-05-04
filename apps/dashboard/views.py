from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.db.models import Count, F, Sum, Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

from apps.stock.models import Product, Category, StockMovement, Cart, Order
from apps.website.models import ContactMessage
from .models import FinancialTransaction, DashboardLog
from .forms import FinancialTransactionForm


def log_action(user, action, description, details=None):
    """Helper to create a DashboardLog entry."""
    DashboardLog.objects.create(
        action=action,
        description=description,
        details=details or {},
        user=user,
    )


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

        # Limité aux 7 derniers mouvements
        recent_movements = StockMovement.objects.select_related("product", "created_by").order_by("-created_at")[:7]
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

        # Quick financial summary for dashboard
        total_revenue = FinancialTransaction.objects.filter(
            transaction_type="revenue"
        ).aggregate(total=Sum("amount"))["total"] or 0
        total_expenses = FinancialTransaction.objects.filter(
            transaction_type="expense"
        ).aggregate(total=Sum("amount"))["total"] or 0

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
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_balance": total_revenue - total_expenses,
        }
        return render(request, "stock/dashboard_home.html", context)


class ComptabiliteView(LoginRequiredMixin, View):
    def get(self, request):
        transactions = FinancialTransaction.objects.select_related("created_by").all()

        # Filters
        tx_type = request.GET.get("type", "")
        category = request.GET.get("category", "")
        search = request.GET.get("q", "")

        if tx_type:
            transactions = transactions.filter(transaction_type=tx_type)
        if category:
            transactions = transactions.filter(category=category)
        if search:
            transactions = transactions.filter(
                Q(reference__icontains=search) | Q(description__icontains=search)
            )

        total_revenue = FinancialTransaction.objects.filter(
            transaction_type="revenue"
        ).aggregate(total=Sum("amount"))["total"] or 0
        total_expenses = FinancialTransaction.objects.filter(
            transaction_type="expense"
        ).aggregate(total=Sum("amount"))["total"] or 0

        total_stock_value = sum(
            p.stock_value for p in Product.objects.filter(is_active=True)
        )

        today = timezone.now()
        start_of_day = today.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        sales_today = FinancialTransaction.objects.filter(
            transaction_type="revenue", created_at__gte=start_of_day
        ).aggregate(total=Sum("amount"))["total"] or 0
        sales_month = FinancialTransaction.objects.filter(
            transaction_type="revenue", created_at__gte=start_of_month
        ).aggregate(total=Sum("amount"))["total"] or 0
        sales_year = FinancialTransaction.objects.filter(
            transaction_type="revenue", created_at__gte=start_of_year
        ).aggregate(total=Sum("amount"))["total"] or 0

        exp_today = FinancialTransaction.objects.filter(
            transaction_type="expense", created_at__gte=start_of_day
        ).aggregate(total=Sum("amount"))["total"] or 0
        exp_month = FinancialTransaction.objects.filter(
            transaction_type="expense", created_at__gte=start_of_month
        ).aggregate(total=Sum("amount"))["total"] or 0
        exp_year = FinancialTransaction.objects.filter(
            transaction_type="expense", created_at__gte=start_of_year
        ).aggregate(total=Sum("amount"))["total"] or 0

        # Monthly stats for the chart (last 6 months)
        monthly_data = []
        for i in range(5, -1, -1):
            month_start = (timezone.now().replace(day=1) - timedelta(days=i * 30)).replace(day=1)
            if i > 0:
                month_end = (timezone.now().replace(day=1) - timedelta(days=(i - 1) * 30)).replace(day=1)
            else:
                month_end = timezone.now()
            rev = FinancialTransaction.objects.filter(
                transaction_type="revenue",
                created_at__gte=month_start,
                created_at__lt=month_end,
            ).aggregate(total=Sum("amount"))["total"] or 0
            exp = FinancialTransaction.objects.filter(
                transaction_type="expense",
                created_at__gte=month_start,
                created_at__lt=month_end,
            ).aggregate(total=Sum("amount"))["total"] or 0
            monthly_data.append({
                "label": month_start.strftime("%b %Y"),
                "revenue": float(rev),
                "expense": float(exp),
            })

        context = {
            "transactions": transactions[:100],
            "form": FinancialTransactionForm(),
            "total_revenue": total_revenue,
            "total_expenses": total_expenses,
            "net_balance": total_revenue - total_expenses,
            "total_stock_value": total_stock_value,
            "sales_today": sales_today,
            "sales_month": sales_month,
            "sales_year": sales_year,
            "exp_today": exp_today,
            "exp_month": exp_month,
            "exp_year": exp_year,
            "tx_count": transactions.count(),
            "selected_type": tx_type,
            "selected_category": category,
            "search": search,
            "monthly_data": monthly_data,
            "category_choices": FinancialTransaction.CATEGORY_CHOICES,
        }
        return render(request, "dashboard/comptabilite.html", context)

    def post(self, request):
        form = FinancialTransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.created_by = request.user
            tx.save()
            action_type = "revenue_add" if tx.transaction_type == "revenue" else "expense_add"
            log_action(
                request.user,
                action_type,
                f"{tx.get_transaction_type_display()} de {tx.amount} GNF — {tx.get_category_display()}",
                {"reference": tx.reference, "amount": str(tx.amount), "category": tx.category},
            )
            messages.success(request, f"Transaction « {tx.reference} » enregistrée avec succès.")
        else:
            messages.error(request, "Erreur lors de l'enregistrement de la transaction.")
        return redirect("dashboard:comptabilite")


class TransactionDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tx = get_object_or_404(FinancialTransaction, pk=pk)
        ref = tx.reference
        log_action(
            request.user,
            "transaction_delete",
            f"Suppression de la transaction {ref} ({tx.get_transaction_type_display()} — {tx.amount} GNF)",
            {"reference": ref, "amount": str(tx.amount)},
        )
        tx.delete()
        messages.success(request, f"Transaction « {ref} » supprimée.")
        return redirect("dashboard:comptabilite")


class HistoriquesView(LoginRequiredMixin, View):
    def get(self, request):
        logs = DashboardLog.objects.select_related("user").all()

        # Filters
        action = request.GET.get("action", "")
        search = request.GET.get("q", "")

        if action:
            logs = logs.filter(action=action)
        if search:
            logs = logs.filter(description__icontains=search)

        context = {
            "logs": logs[:200],
            "total_logs": logs.count(),
            "selected_action": action,
            "search": search,
            "action_choices": DashboardLog.ACTION_TYPES,
        }
        return render(request, "dashboard/historiques.html", context)


class LogDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        log = get_object_or_404(DashboardLog, pk=pk)
        data = {
            "id": log.pk,
            "action": log.get_action_display(),
            "action_code": log.action,
            "description": log.description,
            "details": log.details,
            "user": log.user.get_full_name() or log.user.username if log.user else "Système",
            "created_at": log.created_at.strftime("%d/%m/%Y à %H:%M:%S"),
        }
        return JsonResponse(data)
