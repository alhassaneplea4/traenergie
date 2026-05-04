from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.db.models import Q

from .models import Product, Category, CartItem, Cart, StockMovement
from .forms import ProductForm, StockMovementForm


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
        movements = StockMovement.objects.select_related("product", "created_by").order_by("-created_at")[:50]
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
def cart_checkout(request):
    """Convert cart to a stock-out movement for each item."""
    if request.method != "POST":
        return redirect("dashboard:cart")
    cart, _ = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, "Votre panier est vide.")
        return redirect("dashboard:cart")

    for item in cart.items.select_related("product").all():
        if item.quantity > item.product.quantity_in_stock:
            messages.error(request, f"Stock insuffisant pour {item.product.name}.")
            return redirect("dashboard:cart")
        StockMovement.objects.create(
            product=item.product,
            movement_type="out",
            quantity=item.quantity,
            reason=f"Sortie panier — {request.user.get_full_name() or request.user.username}",
            created_by=request.user,
        )
    cart.clear()
    messages.success(request, "Sortie de stock validée avec succès.")
    return redirect("dashboard:cart")
