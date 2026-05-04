from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={
                "placeholder": "Votre nom complet",
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition",
            }),
            "email": forms.EmailInput(attrs={
                "placeholder": "votre@email.com",
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition",
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "+224 00 00 00 00",
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition",
            }),
            "subject": forms.TextInput(attrs={
                "placeholder": "Objet de votre message",
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition",
            }),
            "message": forms.Textarea(attrs={
                "placeholder": "Décrivez votre besoin...",
                "rows": 5,
                "class": "w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition resize-none",
            }),
        }
