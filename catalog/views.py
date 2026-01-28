import json
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Tire, Disk


def about(request):
    """About us page."""
    return render(request, "catalog/about.html")


def delivery(request):
    """Delivery and payment page."""
    return render(request, "catalog/delivery.html")


def pre_order(request):
    """Pre-order page."""
    return render(request, "catalog/pre_order.html")


def contacts(request):
    """Contacts page."""
    return render(request, "catalog/contacts.html")


def index(request):
    """
    Home page view.
    Shows featured tires and filter options for quick search.
    """
    from .models import Brand

    featured_tires = Tire.objects.filter(in_stock=True)[:4]

    # Filter options for tires (use set() for unique values)
    all_tires = Tire.objects.all()
    tire_filters = {
        "diameters": sorted(set(all_tires.values_list("diameter", flat=True))),
        "widths": sorted(set(all_tires.values_list("width", flat=True))),
        "profiles": sorted(set(all_tires.values_list("profile", flat=True))),
        "seasons": Tire.SEASON_CHOICES,
        "brands": Brand.objects.filter(tires__isnull=False).distinct().order_by("name"),
    }

    # Filter options for disks (use set() for unique values)
    all_disks = Disk.objects.all()
    disk_filters = {
        "diameters": sorted(set(all_disks.values_list("diameter", flat=True))),
        "widths": sorted(set(all_disks.values_list("width", flat=True))),
        "pcds": sorted(set(all_disks.values_list("pcd", flat=True))),
        "types": Disk.TYPE_CHOICES,
        "brands": Brand.objects.filter(disks__isnull=False).distinct().order_by("name"),
    }

    context = {
        "featured_tires": featured_tires,
        "tire_filters": tire_filters,
        "disk_filters": disk_filters,
    }
    return render(request, "catalog/index.html", context)


def tire_list(request):
    """List of all tires with pagination and filters."""
    tires_qs = Tire.objects.select_related("brand").all()

    # Get filter values from request
    diameter = request.GET.get("diameter")
    width = request.GET.get("width")
    profile = request.GET.get("profile")
    season = request.GET.get("season")
    brand = request.GET.get("brand")
    load_index = request.GET.get("load_index")
    speed_index = request.GET.get("speed_index")

    # Apply filters
    if diameter:
        tires_qs = tires_qs.filter(diameter=diameter)
    if width:
        tires_qs = tires_qs.filter(width=width)
    if profile:
        tires_qs = tires_qs.filter(profile=profile)
    if season:
        tires_qs = tires_qs.filter(season=season)
    if brand:
        tires_qs = tires_qs.filter(brand__slug=brand)
    if load_index:
        tires_qs = tires_qs.filter(load_index=load_index)
    if speed_index:
        tires_qs = tires_qs.filter(speed_index=speed_index)

    # Get unique values for filter dropdowns (use set() for SQLite compatibility)
    from .models import Brand
    all_tires = Tire.objects.all()
    filter_options = {
        "diameters": sorted(set(all_tires.values_list("diameter", flat=True))),
        "widths": sorted(set(all_tires.values_list("width", flat=True))),
        "profiles": sorted(set(all_tires.values_list("profile", flat=True))),
        "seasons": Tire.SEASON_CHOICES,
        "brands": Brand.objects.filter(tires__isnull=False).distinct().order_by("name"),
        "load_indices": sorted(set(all_tires.values_list("load_index", flat=True))),
        "speed_indices": sorted(set(all_tires.values_list("speed_index", flat=True))),
    }

    # Current filter values for template
    current_filters = {
        "diameter": diameter or "",
        "width": width or "",
        "profile": profile or "",
        "season": season or "",
        "brand": brand or "",
        "load_index": load_index or "",
        "speed_index": speed_index or "",
    }

    paginator = Paginator(tires_qs, 15)
    page_number = request.GET.get("page")
    tires = paginator.get_page(page_number)

    context = {
        "tires": tires,
        "filter_options": filter_options,
        "current_filters": current_filters,
    }
    return render(request, "catalog/tire_list.html", context)


def disk_list(request):
    """List of all disks with pagination and filters."""
    disks_qs = Disk.objects.select_related("brand").all()

    # Get filter values from request
    diameter = request.GET.get("diameter")
    width = request.GET.get("width")
    pcd = request.GET.get("pcd")
    dia = request.GET.get("dia")
    et = request.GET.get("et")
    disk_type = request.GET.get("type")
    brand = request.GET.get("brand")

    # Apply filters
    if diameter:
        disks_qs = disks_qs.filter(diameter=diameter)
    if width:
        disks_qs = disks_qs.filter(width=width)
    if pcd:
        disks_qs = disks_qs.filter(pcd=pcd)
    if dia:
        disks_qs = disks_qs.filter(dia=dia)
    if et:
        disks_qs = disks_qs.filter(et=et)
    if disk_type:
        disks_qs = disks_qs.filter(disk_type=disk_type)
    if brand:
        disks_qs = disks_qs.filter(brand__slug=brand)

    # Get unique values for filter dropdowns (use set() for SQLite compatibility)
    from .models import Brand
    all_disks = Disk.objects.all()
    filter_options = {
        "diameters": sorted(set(all_disks.values_list("diameter", flat=True))),
        "widths": sorted(set(all_disks.values_list("width", flat=True))),
        "pcds": sorted(set(all_disks.values_list("pcd", flat=True))),
        "dias": sorted(set(all_disks.values_list("dia", flat=True))),
        "ets": sorted(set(all_disks.values_list("et", flat=True))),
        "types": Disk.TYPE_CHOICES,
        "brands": Brand.objects.filter(disks__isnull=False).distinct().order_by("name"),
    }

    # Current filter values for template
    current_filters = {
        "diameter": diameter or "",
        "width": width or "",
        "pcd": pcd or "",
        "dia": dia or "",
        "et": et or "",
        "type": disk_type or "",
        "brand": brand or "",
    }

    paginator = Paginator(disks_qs, 15)
    page_number = request.GET.get("page")
    disks = paginator.get_page(page_number)

    context = {
        "disks": disks,
        "filter_options": filter_options,
        "current_filters": current_filters,
    }
    return render(request, "catalog/disk_list.html", context)


def tire_detail(request, slug):
    """Detail page for a single tire."""
    tire = get_object_or_404(Tire, slug=slug)
    return render(request, "catalog/tire_detail.html", {"tire": tire})


def disk_detail(request, slug):
    """Detail page for a single disk."""
    disk = get_object_or_404(Disk, slug=slug)
    return render(request, "catalog/disk_detail.html", {"disk": disk})


def search(request):
    """Search tires and disks."""
    query = request.GET.get("q", "").strip()
    tires = []
    disks = []

    if query:
        # Search tires by brand name, model name, or article
        tires = Tire.objects.filter(
            Q(brand__name__icontains=query) |
            Q(model_name__icontains=query) |
            Q(article__icontains=query)
        )[:20]

        # Search disks by brand name, model name, article, or color
        disks = Disk.objects.filter(
            Q(brand__name__icontains=query) |
            Q(model_name__icontains=query) |
            Q(article__icontains=query) |
            Q(color__icontains=query)
        )[:20]

    context = {
        "query": query,
        "tires": tires,
        "disks": disks,
        "total_count": len(tires) + len(disks),
    }
    return render(request, "catalog/search.html", context)


# ─── Cart Functions ─────────────────────────────────────
def get_cart(request):
    """Get cart from session."""
    return request.session.get("cart", {"tires": {}, "disks": {}})


def save_cart(request, cart):
    """Save cart to session."""
    request.session["cart"] = cart
    request.session.modified = True


def cart_view(request):
    """Display cart contents."""
    cart = get_cart(request)

    # Get tire objects
    tire_items = []
    for tire_id, qty in cart.get("tires", {}).items():
        try:
            tire = Tire.objects.get(id=tire_id)
            tire_items.append({
                "product": tire,
                "quantity": qty,
                "total": tire.price * qty,
                "type": "tire",
            })
        except Tire.DoesNotExist:
            pass

    # Get disk objects
    disk_items = []
    for disk_id, qty in cart.get("disks", {}).items():
        try:
            disk = Disk.objects.get(id=disk_id)
            disk_items.append({
                "product": disk,
                "quantity": qty,
                "total": disk.price * qty,
                "type": "disk",
            })
        except Disk.DoesNotExist:
            pass

    items = tire_items + disk_items
    total = sum(item["total"] for item in items)

    context = {
        "items": items,
        "total": total,
        "item_count": sum(cart.get("tires", {}).values()) + sum(cart.get("disks", {}).values()),
    }
    return render(request, "catalog/cart.html", context)


@require_POST
def cart_add(request):
    """Add item to cart (AJAX)."""
    try:
        data = json.loads(request.body)
        product_type = data.get("type")  # "tire" or "disk"
        product_id = str(data.get("id"))
        quantity = int(data.get("quantity", 1))

        cart = get_cart(request)

        if product_type == "tire":
            if not Tire.objects.filter(id=product_id).exists():
                return JsonResponse({"success": False, "error": "Товар не знайдено"})
            cart_key = "tires"
        elif product_type == "disk":
            if not Disk.objects.filter(id=product_id).exists():
                return JsonResponse({"success": False, "error": "Товар не знайдено"})
            cart_key = "disks"
        else:
            return JsonResponse({"success": False, "error": "Невірний тип товару"})

        if product_id in cart[cart_key]:
            cart[cart_key][product_id] += quantity
        else:
            cart[cart_key][product_id] = quantity

        save_cart(request, cart)

        total_items = sum(cart.get("tires", {}).values()) + sum(cart.get("disks", {}).values())

        return JsonResponse({
            "success": True,
            "message": "Товар додано до кошика",
            "cart_count": total_items,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def cart_update(request):
    """Update item quantity in cart (AJAX)."""
    try:
        data = json.loads(request.body)
        product_type = data.get("type")
        product_id = str(data.get("id"))
        quantity = int(data.get("quantity", 1))

        cart = get_cart(request)
        cart_key = "tires" if product_type == "tire" else "disks"

        if quantity > 0:
            cart[cart_key][product_id] = quantity
        else:
            cart[cart_key].pop(product_id, None)

        save_cart(request, cart)

        total_items = sum(cart.get("tires", {}).values()) + sum(cart.get("disks", {}).values())

        return JsonResponse({
            "success": True,
            "cart_count": total_items,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def cart_remove(request):
    """Remove item from cart (AJAX)."""
    try:
        data = json.loads(request.body)
        product_type = data.get("type")
        product_id = str(data.get("id"))

        cart = get_cart(request)
        cart_key = "tires" if product_type == "tire" else "disks"

        cart[cart_key].pop(product_id, None)
        save_cart(request, cart)

        total_items = sum(cart.get("tires", {}).values()) + sum(cart.get("disks", {}).values())

        return JsonResponse({
            "success": True,
            "cart_count": total_items,
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def cart_count(request):
    """Get cart item count (for AJAX updates)."""
    cart = get_cart(request)
    total_items = sum(cart.get("tires", {}).values()) + sum(cart.get("disks", {}).values())
    return JsonResponse({"count": total_items})
