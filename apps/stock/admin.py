from django.contrib import admin
from .models import Category, Unit, Supplier, Product, StockMovement, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "color", "product_count"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ["name", "abbreviation"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "phone", "is_active"]
    list_filter = ["is_active"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "category", "unit_price", "quantity_in_stock", "is_low_stock", "is_active"]
    list_filter = ["category", "is_active"]
    search_fields = ["name", "sku"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ["product", "movement_type", "quantity", "created_by", "created_at"]
    list_filter = ["movement_type"]
    readonly_fields = ["created_at"]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "total_items", "total_price", "updated_at"]
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["reference", "supplier", "status", "total", "created_by", "created_at"]
    list_filter = ["status"]
    inlines = [OrderItemInline]
    readonly_fields = ["reference", "created_at", "updated_at"]
