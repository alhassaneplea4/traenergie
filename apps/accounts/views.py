from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views import View


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

