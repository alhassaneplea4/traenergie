from django import forms
from .models import FinancialTransaction

INPUT_CLASS = "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition"
SELECT_CLASS = "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500 transition"


class FinancialTransactionForm(forms.ModelForm):
    class Meta:
        model = FinancialTransaction
        fields = ["transaction_type", "category", "amount", "description"]
        widgets = {
            "transaction_type": forms.Select(attrs={"class": SELECT_CLASS}),
            "category": forms.Select(attrs={"class": SELECT_CLASS}),
            "amount": forms.NumberInput(attrs={"class": INPUT_CLASS, "placeholder": "Montant en GNF", "min": "0", "step": "0.01"}),
            "description": forms.Textarea(attrs={"class": INPUT_CLASS, "rows": 3, "placeholder": "Description de la transaction..."}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")
        return amount
