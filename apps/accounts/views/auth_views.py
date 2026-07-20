from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.views import View

from apps.core.exceptions import DomainError

from ..services import AuthService


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        service = AuthService()
        try:
            user = service.authenticate_user(
                username=request.POST.get("username", "").strip(),
                password=request.POST.get("password", ""),
            )
        except DomainError as exc:
            return render(request, self.template_name, {"error": exc.message})

        login(request, user)
        return redirect("core:home")


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect("core:home")

    def get(self, request):
        logout(request)
        return redirect("core:home")


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        service = AuthService()
        try:
            user = service.create_customer_with_password(
                username=request.POST.get("username", "").strip(),
                password=request.POST.get("password", ""),
                phone=request.POST.get("phone", "").strip(),
                first_name=request.POST.get("first_name", "").strip(),
                last_name=request.POST.get("last_name", "").strip(),
            )
        except DomainError as exc:
            return render(request, self.template_name, {"error": exc.message})

        login(request, user)
        return redirect("core:home")
