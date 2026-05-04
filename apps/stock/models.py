from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default="cyan", verbose_name="Couleur")
    icon = models.CharField(max_length=50, default="box", verbose_name="Icône")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def product_count(self):
        return self.products.count()


class Unit(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nom")
    abbreviation = models.CharField(max_length=10, verbose_name="Abréviation")

    class Meta:
        verbose_name = "Unité"
        verbose_name_plural = "Unités"

    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Supplier(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nom")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products", verbose_name="Catégorie"
    )
    unit = models.ForeignKey(
        Unit, on_delete=models.PROTECT, related_name="products", verbose_name="Unité", null=True, blank=True
    )
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name="Fournisseur"
    )
    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    sku = models.CharField(max_length=100, unique=True, verbose_name="Référence SKU")
    description = models.TextField(blank=True, verbose_name="Description")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Image")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix unitaire (FCFA)")
    quantity_in_stock = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    min_stock_level = models.PositiveIntegerField(default=5, verbose_name="Stock minimum d'alerte")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} [{self.sku}]"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.min_stock_level

    @property
    def stock_value(self):
        return self.unit_price * self.quantity_in_stock

    @property
    def stock_status(self):
        if self.quantity_in_stock == 0:
            return "out"
        if self.is_low_stock:
            return "low"
        return "ok"


class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ("in", "Entrée"),
        ("out", "Sortie"),
        ("adjustment", "Ajustement"),
        ("return", "Retour"),
    ]
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="movements", verbose_name="Produit"
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES, verbose_name="Type")
    quantity = models.IntegerField(verbose_name="Quantité")
    reason = models.CharField(max_length=300, blank=True, verbose_name="Motif")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="movements", verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()} — {self.product.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        if not self.pk:
            with transaction.atomic():
                # select_for_update locks the row so concurrent saves don't double-count
                product = Product.objects.select_for_update().get(pk=self.product_id)
                if self.movement_type in ("in", "return"):
                    product.quantity_in_stock += self.quantity
                elif self.movement_type == "out":
                    product.quantity_in_stock = max(0, product.quantity_in_stock - self.quantity)
                elif self.movement_type == "adjustment":
                    product.quantity_in_stock = self.quantity
                product.save()
                self.product = product
                super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart", verbose_name="Utilisateur"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"

    def __str__(self):
        return f"Panier de {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    def clear(self):
        self.items.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantité")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        unique_together = ["cart", "product"]

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.product.unit_price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ("draft", "Brouillon"),
        ("confirmed", "Confirmée"),
        ("delivered", "Livrée"),
        ("cancelled", "Annulée"),
    ]
    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence")
    supplier = models.ForeignKey(
        Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fournisseur"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Commande #{self.reference}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.order_items.all())

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"CMD-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit")
    quantity = models.PositiveIntegerField(verbose_name="Quantité")
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix unitaire")

    class Meta:
        verbose_name = "Article de commande"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
