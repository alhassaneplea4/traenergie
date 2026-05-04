from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return render(request, "accounts/login.html")

    def post(self, request):
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get("next", "dashboard:home")
            return redirect(next_url)
        messages.error(request, "Identifiant ou mot de passe incorrect.")
        return render(request, "accounts/login.html", {"username": username})


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("website:home")


class RegisterView(View):
    def get(self, request):
        return render(request, "accounts/register.html")

    def post(self, request):
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")

        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return render(request, "accounts/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return render(request, "accounts/register.html")

        user = User.objects.create_user(
            username=username, email=email, password=password1,
            first_name=first_name, last_name=last_name
        )
        login(request, user)
        messages.success(request, f"Bienvenue, {user.first_name or user.username} !")
        return redirect("dashboard:home")
