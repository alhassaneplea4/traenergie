from django import forms
from .models import Product, StockMovement, Category, Supplier


INPUT_CLASS = "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition"
SELECT_CLASS = "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500 transition"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "sku", "category", "unit", "supplier", "description", "image", "unit_price", "quantity_in_stock", "min_stock_level", "is_active"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Nom du produit"}),
            "sku": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Ex: CABLE-HTA-16MM"}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3}),
            "unit_price": forms.NumberInput(attrs={"class": INPUT_CLASS, "step": "0.01"}),
            "quantity_in_stock": forms.NumberInput(attrs={"class": INPUT_CLASS}),
            "min_stock_level": forms.NumberInput(attrs={"class": INPUT_CLASS}),
            "category": forms.Select(attrs={"class": SELECT_CLASS}),
            "unit": forms.Select(attrs={"class": SELECT_CLASS}),
            "supplier": forms.Select(attrs={"class": SELECT_CLASS}),
            "is_active": forms.CheckboxInput(attrs={"class": "w-4 h-4 text-cyan-500 rounded border-slate-600"}),
        }


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ["product", "movement_type", "quantity", "reason"]
        widgets = {
            "product": forms.Select(attrs={"class": SELECT_CLASS}),
            "movement_type": forms.Select(attrs={"class": SELECT_CLASS}),
            "quantity": forms.NumberInput(attrs={"class": INPUT_CLASS, "min": 1}),
            "reason": forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Motif du mouvement"}),
        }

    def clean_quantity(self):
        qty = self.cleaned_data.get("quantity")
        if qty is not None and qty <= 0:
            raise forms.ValidationError("La quantité doit être supérieure à 0.")
        return qty


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug", "description", "color", "icon"]
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "slug": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 2}),
            "color": forms.TextInput(attrs={"class": INPUT_CLASS}),
            "icon": forms.TextInput(attrs={"class": INPUT_CLASS}),
        }
