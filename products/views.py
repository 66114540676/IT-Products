from django.shortcuts import render, get_object_or_404
from dashboard.models import Product, Category


# ------------------------- แสดงรายการสินค้า -------------------------
def product_list(request):
    # ดึงค่าค้นหาจาก Query string เช่น ?q=mouse
    q = (request.GET.get("q") or "").strip()

    # ดึง id หมวดหมู่ เช่น ?category=2
    category_id = request.GET.get("category")

    # ดึงข้อมูลสินค้า พร้อมข้อมูลหมวดหมู่ (ใช้ select_related เพื่อลดจำนวน query)
    qs = Product.objects.select_related("category")

    # ---------- กรองตามหมวด ----------
    active_category = None
    if category_id:
        # ถ้า category_id มีค่า → ดึงหมวดหมู่จากฐานข้อมูล
        # ถ้าไม่เจอ → แสดงหน้า 404
        active_category = get_object_or_404(Category, pk=category_id)

        # กรองสินค้าทั้งหมดให้เหลือเฉพาะหมวดนั้น
        qs = qs.filter(category=active_category)

    # ---------- ค้นหาชื่อสินค้า ----------
    if q:
        # ถ้ามีคำค้นหา → ค้นในฟิลด์ name แบบไม่สนตัวพิมพ์เล็กใหญ่
        qs = qs.filter(name__icontains=q)

    # ---------- เรียงลำดับสินค้า ----------
    # เรียงตาม id (เรียงจากสินค้าที่เพิ่มเข้ามาก่อนหลัง)
    qs = qs.order_by("id")

    # ---------- ดึงหมวดหมู่ทั้งหมด ----------
    # พยายามเรียงตาม created_at ถ้ามี field นี้
    try:
        categories = Category.objects.order_by("created_at", "id")
    except Exception:
        # ถ้าไม่มีฟิลด์ created_at ให้เรียงตาม id แทน
        categories = Category.objects.order_by("id")

    # เก็บผลลัพธ์สุดท้ายของสินค้าไว้ในตัวแปร products
    products = qs

    # ---------- เตรียมข้อมูลส่งให้เทมเพลต ----------
    ctx = {
        "products": products,                      # รายการสินค้า
        "categories": categories,                  # รายการหมวดหมู่ทั้งหมด
        "q": q,                                    # ค่าค้นหาปัจจุบัน
        "active_category": str(active_category.id) if active_category else "",  # หมวดที่เลือกอยู่
    }

    # ส่งข้อมูลไปยังเทมเพลต product_list.html
    return render(request, "products/product_list.html", ctx)


# ------------------------- แสดงรายละเอียดสินค้า -------------------------
def product_detail(request, pk):
    # ดึงสินค้าตามรหัส pk (Primary Key)
    # ถ้าไม่พบสินค้าจะขึ้นหน้า 404 อัตโนมัติ
    product = get_object_or_404(Product, pk=pk)

    # ส่งข้อมูลสินค้าไปยังเทมเพลต product_detail.html
    return render(request, "products/product_detail.html", {"product": product})
