from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .models import Service, Project, TeamMember, Testimonial, CompanyInfo
from .forms import ContactForm


class HomeView(View):
    def get(self, request):
        context = {
            "company": CompanyInfo.get_instance(),
            "services": Service.objects.filter(is_active=True),
            "projects": Project.objects.filter(is_featured=True)[:6],
            "team": TeamMember.objects.filter(is_active=True),
            "testimonials": Testimonial.objects.filter(is_active=True),
            "contact_form": ContactForm(),
        }
        return render(request, "website/home.html", context)


class ContactView(View):
    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a bien été envoyé. Nous vous répondrons sous 24h.")
            return redirect("website:home")
        messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
        context = {
            "company": CompanyInfo.get_instance(),
            "services": Service.objects.filter(is_active=True),
            "projects": Project.objects.filter(is_featured=True)[:6],
            "team": TeamMember.objects.filter(is_active=True),
            "testimonials": Testimonial.objects.filter(is_active=True),
            "contact_form": form,
        }
        return render(request, "website/home.html", context)
