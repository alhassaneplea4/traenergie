from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ("revenue", "Recette"),
        ("expense", "Dépense"),
    ]
    CATEGORY_CHOICES = [
        ("vente", "Vente de produits"),
        ("service", "Prestation de service"),
        ("achat_stock", "Achat de stock"),
        ("salaire", "Salaire"),
        ("loyer", "Loyer"),
        ("transport", "Transport"),
        ("maintenance", "Maintenance"),
        ("autre", "Autre"),
    ]

    reference = models.CharField(max_length=50, unique=True, verbose_name="Référence")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Type")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="autre", verbose_name="Catégorie")
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Montant (GNF)")
    description = models.TextField(blank=True, verbose_name="Description")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="financial_transactions", verbose_name="Créé par"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction financière"
        verbose_name_plural = "Transactions financières"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_transaction_type_display()} #{self.reference} — {self.amount} GNF"

    def save(self, *args, **kwargs):
        if not self.reference:
            prefix = "REC" if self.transaction_type == "revenue" else "DEP"
            self.reference = f"{prefix}-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)


class DashboardLog(models.Model):
    ACTION_TYPES = [
        ("product_create", "Création de produit"),
        ("product_update", "Modification de produit"),
        ("product_delete", "Suppression de produit"),
        ("stock_in", "Entrée de stock"),
        ("stock_out", "Sortie de stock"),
        ("stock_adjust", "Ajustement de stock"),
        ("stock_return", "Retour de stock"),
        ("cart_checkout", "Validation de panier"),
        ("revenue_add", "Ajout de recette"),
        ("expense_add", "Ajout de dépense"),
        ("transaction_delete", "Suppression de transaction"),
        ("other", "Autre"),
    ]

    action = models.CharField(max_length=30, choices=ACTION_TYPES, verbose_name="Action")
    description = models.TextField(verbose_name="Description")
    details = models.JSONField(default=dict, blank=True, verbose_name="Détails")
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="dashboard_logs", verbose_name="Utilisateur"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal d'activités"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_action_display()}] {self.description[:60]}"
