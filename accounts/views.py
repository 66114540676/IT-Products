from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .forms import DeleteAccountForm
from django.db import transaction

# ---- Third-party
from allauth.socialaccount.models import SocialAccount

# ---- Local apps
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile


# ------------------------------------------------------------
# Home
# ------------------------------------------------------------
def home_view(request):
    return render(request, "home/home.html")


# ------------------------------------------------------------
# Authentication: Login / Register / Logout
# ------------------------------------------------------------
def login_view(request):
    """เข้าสู่ระบบด้วย username/password"""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            # ให้มี Profile เสมอ
            Profile.objects.get_or_create(user=user)
            login(request, user)
            return redirect("accounts:home")

        messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    return render(request, "accounts/login.html")

"""สมัครสมาชิกใหม่"""
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        avatar = request.FILES.get('avatar')

        if not username or not email or not password1 or not password2:
            messages.error(request, "กรุณากรอกข้อมูลให้ครบทุกช่อง")
        elif password1 != password2:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "ชื่อผู้ใช้นี้ถูกใช้ไปแล้ว")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            Profile.objects.update_or_create(
                user=user,
                defaults={"phone": phone, "address": address},
            )

            messages.success(request, "สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
            return redirect("accounts:login")

    return render(request, "accounts/register.html")


def logout_view(request):
    """ออกจากระบบ"""
    logout(request)
    return redirect("accounts:home")


# ------------------------------------------------------------
# Profile
# ------------------------------------------------------------
@login_required
def account_profile(request):
    providers = list(
        SocialAccount.objects.filter(user=request.user).values_list(
            "provider", flat=True
        )
    )
    login_via = request.session.get("login_via")

    return render(
        request,
        "accounts/account_profile.html",
        {"providers": providers, "login_via": login_via},
    )


@login_required
def account_edit(request):
    if request.method == "POST":
        uform = UserUpdateForm(request.POST, instance=request.user)
        pform = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "อัปเดตโปรไฟล์เรียบร้อย")
            return redirect("accounts:account_edit")
    else:
        uform = UserUpdateForm(instance=request.user)
        pform = ProfileUpdateForm(instance=request.user.profile)

    return render(
        request,
        "accounts/account_edit.html",
        {"uform": uform, "pform": pform},
    )

@login_required
def account_delete(request):
    if request.method == "POST":
        form = DeleteAccountForm(request.POST, user=request.user)
        if form.is_valid():
            with transaction.atomic():
                user = request.user
                logout(request)               
                user.delete()                  
            messages.success(request, "ลบบัญชีผู้ใช้เรียบร้อยแล้ว")
            return redirect("accounts:home")   
    else:
        form = DeleteAccountForm(user=request.user)

    return render(request, "accounts/account_delete.html", {"form": form})

# ------------------------------------------------------------
# Password Change (CBV)
# ------------------------------------------------------------
class AccountPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/account_password_change.html"
    success_url = reverse_lazy("accounts:account_profile")

    def form_valid(self, form):
        messages.success(self.request, "เปลี่ยนรหัสผ่านเรียบร้อย")
        return super().form_valid(form)
