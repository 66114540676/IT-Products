from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

# ---- Local imports ----
from .models import Category, Product


# ----------------------------- Helpers -----------------------------
def _extract_specs(request):
    """ดึง key/value ของสเปกสินค้าจากฟอร์มแล้วคืน dict ที่กรองช่องว่างแล้ว"""
    keys = request.POST.getlist("spec_key[]")
    values = request.POST.getlist("spec_value[]")
    return {k: v for k, v in zip(keys, values) if k and v}


# ----------------------------- Dashboard -----------------------------
@staff_member_required
def dashboard_home(request):
    UserModel = get_user_model()
    ctx = {
        "products_count": Product.objects.count(),
        "categories_count": Category.objects.count(),
        "users_count": UserModel.objects.count(),
    }
    return render(request, "dashboard/dashboard_home.html", ctx)


@staff_member_required
def user_list(request):
    UserModel = get_user_model()
    users = UserModel.objects.order_by("-date_joined")
    return render(request, "dashboard/user_list.html", {"users": users})


# ----------------------------- Products -----------------------------
@staff_member_required
def product_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Product.objects.select_related("category")
    if q:
        qs = qs.filter(name__icontains=q)

    return render(
        request,
        "dashboard/products/product_list.html",
        {"products": qs, "q": q},
    )


@staff_member_required
def product_add(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        description = (request.POST.get("description") or "").strip()
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        category = get_object_or_404(Category, id=category_id) if category_id else None

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category,
            image=image,
            specs=_extract_specs(request),
            created_by=request.user,
            updated_by=request.user,
        )
        messages.success(request, "เพิ่มสินค้าเรียบร้อย ✅")
        return redirect("dashboard:product_list")

    categories = Category.objects.all()
    return render(
        request,
        "dashboard/products/product_add.html",
        {"categories": categories},
    )


@staff_member_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()

    if request.method == "POST":
        product.name = (request.POST.get("name") or "").strip()
        product.description = (request.POST.get("description") or "").strip()
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")

        category_id = request.POST.get("category")
        product.category = (
            get_object_or_404(Category, pk=category_id) if category_id else None
        )

        if request.FILES.get("image"):
            product.image = request.FILES["image"]

        product.specs = _extract_specs(request)
        product.updated_by = request.user
        product.save()

        messages.success(request, "แก้ไขสินค้าเรียบร้อยแล้ว ✅")
        return redirect("dashboard:product_list")

    return render(
        request,
        "dashboard/products/product_edit.html",
        {"product": product, "categories": categories},
    )


@staff_member_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        messages.success(request, "ลบสินค้าเรียบร้อย")
        return redirect("dashboard:product_list")
    return render(
        request,
        "dashboard/products/product_confirm_delete.html",
        {"product": product},
    )


# ----------------------------- Categories -----------------------------
@staff_member_required
def category_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = Category.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q))
    return render(
        request,
        "dashboard/categories/category_list.html",
        {"categories": qs, "q": q},
    )


@staff_member_required
def category_add(request):
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        if name:
            Category.objects.create(
                name=name, created_by=request.user, updated_by=request.user
            )
            messages.success(request, "เพิ่มหมวดหมู่เรียบร้อย ✅")
        return redirect("dashboard:category_list")
    return render(request, "dashboard/categories/category_add.html")


@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        name = (request.POST.get("name") or "").strip()
        if name:
            category.name = name
            category.updated_by = request.user
            category.save()
            messages.success(request, "บันทึกหมวดหมู่เรียบร้อย ✅")
        return redirect("dashboard:category_list")
    return render(
        request,
        "dashboard/categories/category_add.html",
        {"category": category},
    )


@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        category.delete()
        messages.success(request, "ลบหมวดหมู่เรียบร้อย")
        return redirect("dashboard:category_list")
    return render(
        request,
        "dashboard/categories/category_add.html",
        {"category": category},
    )
