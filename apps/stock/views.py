from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.db.models import Q

from .models import Product, Category, CartItem, Cart, StockMovement, Sale, SaleItem
from .forms import ProductForm, StockMovementForm
from apps.dashboard.models import FinancialTransaction
from apps.dashboard.views import log_action


class ProductListView(LoginRequiredMixin, View):
    def get(self, request):
        qs = Product.objects.select_related("category", "unit").filter(is_active=True)
        search = request.GET.get("q", "")
        category_id = request.GET.get("category", "")
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search))
        if category_id:
            qs = qs.filter(category_id=category_id)

        context = {
            "products": qs,
            "categories": Category.objects.all(),
            "search": search,
            "selected_category": category_id,
            "form": ProductForm(),
        }
        if request.htmx:
            return render(request, "stock/partials/product_table.html", context)
        return render(request, "stock/product_list.html", context)


class ProductCreateView(LoginRequiredMixin, View):
    def post(self, request):
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            log_action(
                request.user, "product_create",
                f"Création du produit « {product.name} » (SKU: {product.sku})",
                {"product_id": product.pk, "name": product.name, "sku": product.sku, "price": str(product.unit_price)},
            )
            messages.success(request, f"Produit « {product.name} » créé avec succès.")
            if request.htmx:
                products = Product.objects.select_related("category", "unit").filter(is_active=True)
                return render(request, "stock/partials/product_table.html", {
                    "products": products,
                    "categories": Category.objects.all(),
                    "form": ProductForm(),
                })
        else:
            messages.error(request, "Erreur lors de la création du produit.")
        return redirect("dashboard:products")


class ProductUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(instance=product)
        context = {"form": form, "product": product}
        if request.htmx:
            return render(request, "stock/partials/product_form_modal.html", context)
        # Non-HTMX fallback: full edit page
        return render(request, "stock/product_edit.html", context)

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Produit « {product.name} » mis à jour.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field} : {error}")
        return redirect("dashboard:products")


class ProductDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        name = product.name
        product.is_active = False
        product.save()
        log_action(
            request.user, "product_delete",
            f"Désactivation du produit « {name} » (SKU: {product.sku})",
            {"product_id": product.pk, "name": name, "sku": product.sku},
        )
        messages.success(request, f"Produit « {name} » désactivé.")
        if request.htmx:
            products = Product.objects.select_related("category", "unit").filter(is_active=True)
            return render(request, "stock/partials/product_table.html", {
                "products": products,
                "categories": Category.objects.all(),
                "form": ProductForm(),
            })
        return redirect("dashboard:products")


class StockMovementView(LoginRequiredMixin, View):
    def get(self, request):
        # Limité aux 7 derniers mouvements
        movements = StockMovement.objects.select_related("product", "created_by").order_by("-created_at")[:7]
        context = {
            "movements": movements,
            "form": StockMovementForm(),
        }
        return render(request, "stock/movements.html", context)

    def post(self, request):
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.created_by = request.user
            movement.save()
            # Map movement_type to log action
            action_map = {"in": "stock_in", "out": "stock_out", "adjustment": "stock_adjust", "return": "stock_return"}
            log_action(
                request.user,
                action_map.get(movement.movement_type, "other"),
                f"{movement.get_movement_type_display()} de {movement.quantity} × {movement.product.name}",
                {"product": movement.product.name, "quantity": movement.quantity, "type": movement.movement_type, "reason": movement.reason},
            )
            messages.success(request, "Mouvement de stock enregistré.")
        else:
            messages.error(request, "Erreur dans le formulaire.")
        return redirect("dashboard:stock_movements")


# ── Cart Views ────────────────────────────────────────────────────────────────

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    products = Product.objects.filter(is_active=True, quantity_in_stock__gt=0).select_related("category")
    context = {
        "cart": cart,
        "cart_items": cart.items.select_related("product__category").all(),
        "products": products,
    }
    return render(request, "stock/cart.html", context)


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        if item.quantity < product.quantity_in_stock:
            item.quantity += 1
            item.save()
    if request.htmx:
        context = {
            "cart": cart,
            "cart_items": cart.items.select_related("product__category").all(),
            "products": Product.objects.filter(is_active=True, quantity_in_stock__gt=0).select_related("category"),
        }
        return render(request, "stock/partials/cart_sidebar.html", context)
    # ?next=products redirects back to product list instead of cart page
    if request.GET.get("next") == "products":
        messages.success(request, f"« {product.name} » ajouté au panier.")
        return redirect("dashboard:products")
    return redirect("dashboard:cart")


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    if request.htmx:
        cart = request.user.cart
        context = {
            "cart": cart,
            "cart_items": cart.items.select_related("product__category").all(),
            "products": Product.objects.filter(is_active=True, quantity_in_stock__gt=0).select_related("category"),
        }
        return render(request, "stock/partials/cart_sidebar.html", context)
    return redirect("dashboard:cart")


@login_required
def cart_update_qty(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    qty = int(request.POST.get("quantity", 1))
    if qty <= 0:
        item.delete()
    else:
        item.quantity = min(qty, item.product.quantity_in_stock)
        item.save()
    if request.htmx:
        cart = request.user.cart
        context = {
            "cart": cart,
            "cart_items": cart.items.select_related("product__category").all(),
            "products": Product.objects.filter(is_active=True, quantity_in_stock__gt=0).select_related("category"),
        }
        return render(request, "stock/partials/cart_sidebar.html", context)
    return redirect("dashboard:cart")


@login_required
@login_required
def cart_checkout(request):
    """Convert cart to a stock-out movement for each item and record revenue."""
    if request.method != "POST":
        return redirect("dashboard:cart")
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect("dashboard:cart")

    customer_name = request.POST.get("customer_name", "")
    customer_phone = request.POST.get("customer_phone", "")
    payment_method = request.POST.get("payment_method", "cash")

    # Vérification des stocks d'abord
    for item in cart.items.select_related("product").all():
        if item.quantity > item.product.quantity_in_stock:
            messages.error(request, f"Stock insuffisant pour {item.product.name}.")
            return redirect("dashboard:cart")

    # Création de la Vente (Sale)
    sale = Sale.objects.create(
        customer_name=customer_name,
        customer_phone=customer_phone,
        payment_method=payment_method,
        created_by=request.user,
    )

    total_sale = 0
    product_names = []

    for item in cart.items.select_related("product").all():
        # Créer le détail de la vente
        SaleItem.objects.create(
            sale=sale,
            product=item.product,
            quantity=item.quantity,
            unit_price=item.product.unit_price
        )

        # Mouvement de stock
        StockMovement.objects.create(
            product=item.product,
            movement_type="out",
            quantity=item.quantity,
            reason=f"Vente #{sale.reference} — {request.user.get_full_name() or request.user.username}",
            created_by=request.user,
        )
        total_sale += item.subtotal
        product_names.append(f"{item.product.name} ×{item.quantity}")

    # Mise à jour du total de la vente
    sale.total_amount = total_sale
    sale.save()

    # Create a revenue transaction for this sale
    if total_sale > 0:
        tx = FinancialTransaction.objects.create(
            transaction_type="revenue",
            category="vente",
            amount=total_sale,
            reference=sale.reference,  # Use same reference
            description=f"Vente #{sale.reference} : {', '.join(product_names)}",
            created_by=request.user,
        )
        log_action(
            request.user, "cart_checkout",
            f"Validation de la vente {sale.reference} — {len(product_names)} article(s) pour {total_sale} GNF",
            {"reference": sale.reference, "total": str(total_sale), "products": product_names},
        )

    cart.clear()
    messages.success(request, "Vente validée avec succès. Préparation du reçu...")
    return redirect("dashboard:sale_receipt", pk=sale.pk)


class SaleReceiptView(LoginRequiredMixin, View):
    def get(self, request, pk):
        sale = get_object_or_404(Sale, pk=pk)
        return render(request, "stock/receipt.html", {"sale": sale})

class SaleListView(LoginRequiredMixin, View):
    def get(self, request):
        qs = Sale.objects.select_related("created_by").prefetch_related("items__product").order_by("-created_at")
        search = request.GET.get("q", "")
        if search:
            qs = qs.filter(Q(reference__icontains=search) | Q(customer_name__icontains=search) | Q(customer_phone__icontains=search))
            
        context = {
            "sales": qs[:100],  # Limit to latest 100 for performance
            "search": search,
        }
        return render(request, "stock/sale_list.html", context)
