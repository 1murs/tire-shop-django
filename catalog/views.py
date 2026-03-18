import json
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Tire, Disk, CarFitment, ChatSession, ChatMessage


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

    featured_tires = Tire.objects.filter(is_featured=True)[:8]
    if not featured_tires.exists():
        featured_tires = Tire.objects.filter(in_stock=True).order_by('?')[:8]
    featured_disks = Disk.objects.filter(is_featured=True)[:8]

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
        "featured_disks": featured_disks,
        "tire_filters": tire_filters,
        "disk_filters": disk_filters,
    }
    return render(request, "catalog/index.html", context)


def tire_list(request):
    """List of all tires with pagination and filters."""
    tires_qs = Tire.objects.select_related("brand").all()

    # Get filter values from request
    diameters = request.GET.getlist("diameter")
    widths = request.GET.getlist("width")
    profiles = request.GET.getlist("profile")
    seasons = request.GET.getlist("season")
    brands = request.GET.getlist("brand")
    load_indices = request.GET.getlist("load_index")
    speed_indices = request.GET.getlist("speed_index")
    studdeds = request.GET.getlist("studded")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")

    # Apply filters
    if diameters:
        tires_qs = tires_qs.filter(diameter__in=diameters)
    if widths:
        tires_qs = tires_qs.filter(width__in=widths)
    if profiles:
        tires_qs = tires_qs.filter(profile__in=profiles)
    if seasons:
        tires_qs = tires_qs.filter(season__in=seasons)
    if brands:
        tires_qs = tires_qs.filter(brand__slug__in=brands)
    if load_indices:
        tires_qs = tires_qs.filter(load_index__in=load_indices)
    if speed_indices:
        tires_qs = tires_qs.filter(speed_index__in=speed_indices)
    if studdeds:
        tires_qs = tires_qs.filter(studded__in=studdeds)
    if price_min:
        tires_qs = tires_qs.filter(price__gte=price_min)
    if price_max:
        tires_qs = tires_qs.filter(price__lte=price_max)

    # Get unique values for filter dropdowns (use set() for SQLite compatibility)
    from .models import Brand
    all_tires = Tire.objects.all()
    filter_options = {
        "diameters": sorted(v for v in set(all_tires.values_list("diameter", flat=True)) if v),
        "widths": sorted(v for v in set(all_tires.values_list("width", flat=True)) if v),
        "profiles": sorted(v for v in set(all_tires.values_list("profile", flat=True)) if v),
        "seasons": Tire.SEASON_CHOICES,
        "brands": Brand.objects.filter(tires__isnull=False).distinct().order_by("name"),
        "load_indices": sorted(v for v in set(all_tires.values_list("load_index", flat=True)) if v),
        "speed_indices": sorted(v for v in set(all_tires.values_list("speed_index", flat=True)) if v),
        "studded_choices": Tire.STUDDED_CHOICES,
    }

    # Current filter values for template
    current_filters = {
        "diameters": diameters,
        "widths": widths,
        "profiles": profiles,
        "seasons": seasons,
        "brands": brands,
        "load_indices": load_indices,
        "speed_indices": speed_indices,
        "studdeds": studdeds,
        "price_min": price_min or "",
        "price_max": price_max or "",
    }

    # Build query string for pagination (without page param)
    filter_params = request.GET.copy()
    filter_params.pop("page", None)
    filter_query_string = filter_params.urlencode()

    paginator = Paginator(tires_qs, 15)
    page_number = request.GET.get("page")
    tires = paginator.get_page(page_number)

    context = {
        "tires": tires,
        "filter_options": filter_options,
        "current_filters": current_filters,
        "filter_query_string": filter_query_string,
    }
    return render(request, "catalog/tire_list.html", context)


def disk_list(request):
    """List of all disks with pagination and filters."""
    disks_qs = Disk.objects.select_related("brand").all()

    # Get filter values from request
    diameters = request.GET.getlist("diameter")
    widths = request.GET.getlist("width")
    pcds = request.GET.getlist("pcd")
    dias = request.GET.getlist("dia")
    ets = request.GET.getlist("et")
    disk_types = request.GET.getlist("type")
    brands = request.GET.getlist("brand")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")

    # Apply filters
    if diameters:
        disks_qs = disks_qs.filter(diameter__in=diameters)
    if widths:
        disks_qs = disks_qs.filter(width__in=widths)
    if pcds:
        disks_qs = disks_qs.filter(pcd__in=pcds)
    if dias:
        disks_qs = disks_qs.filter(dia__in=dias)
    if ets:
        disks_qs = disks_qs.filter(et__in=ets)
    if disk_types:
        disks_qs = disks_qs.filter(disk_type__in=disk_types)
    if brands:
        disks_qs = disks_qs.filter(brand__slug__in=brands)
    if price_min:
        disks_qs = disks_qs.filter(price__gte=price_min)
    if price_max:
        disks_qs = disks_qs.filter(price__lte=price_max)

    # Get unique values for filter dropdowns (use set() for SQLite compatibility)
    from .models import Brand
    all_disks = Disk.objects.all()
    filter_options = {
        "diameters": sorted(v for v in set(all_disks.values_list("diameter", flat=True)) if v),
        "widths": sorted(v for v in set(all_disks.values_list("width", flat=True)) if v),
        "pcds": sorted(v for v in set(all_disks.values_list("pcd", flat=True)) if v),
        "dias": sorted(v for v in set(all_disks.values_list("dia", flat=True)) if v),
        "ets": sorted(v for v in set(all_disks.values_list("et", flat=True)) if v),
        "types": Disk.TYPE_CHOICES,
        "brands": Brand.objects.filter(disks__isnull=False).distinct().order_by("name"),
    }

    # Current filter values for template
    current_filters = {
        "diameters": diameters,
        "widths": widths,
        "pcds": pcds,
        "dias": dias,
        "ets": ets,
        "types": disk_types,
        "brands": brands,
        "price_min": price_min or "",
        "price_max": price_max or "",
    }

    # Build query string for pagination (without page param)
    filter_params = request.GET.copy()
    filter_params.pop("page", None)
    filter_query_string = filter_params.urlencode()

    paginator = Paginator(disks_qs, 15)
    page_number = request.GET.get("page")
    disks = paginator.get_page(page_number)

    context = {
        "disks": disks,
        "filter_options": filter_options,
        "current_filters": current_filters,
        "filter_query_string": filter_query_string,
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


@require_POST
def callback_request(request):
    """Handle callback request form submission."""
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        data = json.loads(request.body)
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        question = data.get("question", "").strip()

        if not name or not phone:
            return JsonResponse({"success": False, "error": "Заповніть обов'язкові поля"})

        # Prepare email
        subject = f"Замовлення дзвінка від {name}"
        message = f"""
Нове замовлення дзвінка з сайту КМ/Ч 120

Ім'я: {name}
Телефон: {phone}
Питання: {question if question else "Не вказано"}
        """

        # Try to send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@120.com.ua',
                recipient_list=['info@120.com.ua'],
                fail_silently=False,
            )
        except Exception as e:
            # If email fails, still return success (we can log the request)
            print(f"Email error: {e}")
            # In production, you might want to save to database instead

        return JsonResponse({
            "success": True,
            "message": "Дякуємо! Ми зателефонуємо вам найближчим часом."
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


@require_POST
def one_click_order(request):
    """Handle one-click order form submission."""
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        data = json.loads(request.body)
        product_type = data.get("type", "").strip()
        product_id = data.get("product_id")
        phone = data.get("phone", "").strip()

        if not phone:
            return JsonResponse({"success": False, "error": "Введіть номер телефону"})

        # Get product info
        product_name = "Невідомий товар"
        product_price = "0"

        if product_type == "tire":
            try:
                tire = Tire.objects.select_related("brand").get(id=product_id)
                product_name = f"{tire.brand.name} {tire.model_name} {tire.width}/{tire.profile} R{tire.diameter}"
                product_price = f"{tire.price:.0f}"
            except Tire.DoesNotExist:
                pass
        elif product_type == "disk":
            try:
                disk = Disk.objects.select_related("brand").get(id=product_id)
                product_name = f"{disk.brand.name} {disk.model_name} {disk.width}x{disk.diameter}"
                product_price = f"{disk.price:.0f}"
            except Disk.DoesNotExist:
                pass

        # Prepare email
        subject = f"Замовлення в 1 клік - {product_name}"
        message = f"""
Нове замовлення в 1 клік з сайту КМ/Ч 120

Товар: {product_name}
Ціна: {product_price} ₴
Телефон клієнта: {phone}
        """

        # Try to send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@120.com.ua',
                recipient_list=['info@120.com.ua'],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email error: {e}")

        return JsonResponse({
            "success": True,
            "message": "Дякуємо за замовлення! Ми зателефонуємо вам для підтвердження."
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ===== Tire Calculator =====

def tire_calculator(request):
    """Tire size comparison calculator."""
    return render(request, "catalog/calculator.html")


def calculator_by_car(request):
    """Car fitment selection page."""
    vendors = CarFitment.objects.values_list("vendor", flat=True).distinct().order_by("vendor")
    return render(request, "catalog/calculator_by_car.html", {"vendors": list(vendors)})


def calculator_get_models(request):
    """AJAX: Get car models for selected vendor."""
    vendor = request.GET.get("vendor", "")
    if not vendor:
        return JsonResponse({"models": []})

    models = (
        CarFitment.objects.filter(vendor=vendor)
        .values_list("car", flat=True)
        .distinct()
        .order_by("car")
    )
    return JsonResponse({"models": list(models)})


def calculator_get_years(request):
    """AJAX: Get years for selected vendor and model."""
    vendor = request.GET.get("vendor", "")
    car = request.GET.get("car", "")
    if not vendor or not car:
        return JsonResponse({"years": []})

    years = (
        CarFitment.objects.filter(vendor=vendor, car=car)
        .values_list("year", flat=True)
        .distinct()
        .order_by("year")
    )
    return JsonResponse({"years": list(years)})


def calculator_get_modifications(request):
    """AJAX: Get modifications for selected vendor, model, and year."""
    vendor = request.GET.get("vendor", "")
    car = request.GET.get("car", "")
    year = request.GET.get("year", "")
    if not vendor or not car or not year:
        return JsonResponse({"modifications": []})

    modifications = CarFitment.objects.filter(
        vendor=vendor, car=car, year=year
    ).values("id", "modification")

    return JsonResponse({"modifications": list(modifications)})


def calculator_get_fitment(request):
    """AJAX: Get fitment data for selected car."""
    fitment_id = request.GET.get("id", "")
    if not fitment_id:
        return JsonResponse({"error": "ID not provided"}, status=400)

    try:
        fitment = CarFitment.objects.get(id=fitment_id)
    except CarFitment.DoesNotExist:
        return JsonResponse({"error": "Fitment not found"}, status=404)

    def parse_sizes(text):
        """Parse sizes separated by | and # (front/rear)."""
        if not text:
            return []
        sizes = []
        for item in text.split("|"):
            item = item.strip()
            if not item:
                continue
            if "#" in item:
                parts = item.split("#")
                sizes.append({
                    "front": parts[0].strip(),
                    "rear": parts[1].strip() if len(parts) > 1 else parts[0].strip(),
                    "staggered": True
                })
            else:
                sizes.append({"size": item, "staggered": False})
        return sizes

    data = {
        "car": f"{fitment.vendor} {fitment.car} {fitment.year} {fitment.modification}",
        "pcd": fitment.pcd,
        "center_bore": fitment.center_bore,
        "bolt_type": fitment.bolt_type,
        "tires": {
            "oem": parse_sizes(fitment.oem_tires),
            "replacement": parse_sizes(fitment.replacement_tires),
            "tuning": parse_sizes(fitment.tuning_tires),
        },
        "wheels": {
            "oem": parse_sizes(fitment.oem_wheels),
            "replacement": parse_sizes(fitment.replacement_wheels),
            "tuning": parse_sizes(fitment.tuning_wheels),
        },
    }

    return JsonResponse(data)


# ===== Checkout =====

def checkout(request):
    """Checkout page - order form."""
    cart = get_cart(request)

    # Get cart items
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

    if not items:
        return redirect("catalog:cart")

    total = sum(item["total"] for item in items)
    item_count = sum(cart.get("tires", {}).values()) + sum(cart.get("disks", {}).values())

    context = {
        "items": items,
        "total": total,
        "item_count": item_count,
    }
    return render(request, "catalog/checkout.html", context)


@require_POST
def checkout_submit(request):
    """Process checkout form and send order email."""
    from django.core.mail import send_mail
    from django.conf import settings
    from datetime import datetime

    try:
        data = json.loads(request.body)

        # Get form data
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        email = data.get("email", "").strip()
        delivery = data.get("delivery", "").strip()
        city = data.get("city", "").strip()
        address = data.get("address", "").strip()
        comment = data.get("comment", "").strip()

        # Validate required fields
        if not name or not phone:
            return JsonResponse({"success": False, "error": "Заповніть ім'я та телефон"})

        # Get cart items
        cart = get_cart(request)

        tire_items = []
        for tire_id, qty in cart.get("tires", {}).items():
            try:
                tire = Tire.objects.select_related("brand").get(id=tire_id)
                tire_items.append({
                    "name": f"{tire.brand.name} {tire.model_name} {tire.width}/{tire.profile} R{tire.diameter}",
                    "article": tire.article,
                    "price": tire.price,
                    "quantity": qty,
                    "total": tire.price * qty,
                })
            except Tire.DoesNotExist:
                pass

        disk_items = []
        for disk_id, qty in cart.get("disks", {}).items():
            try:
                disk = Disk.objects.select_related("brand").get(id=disk_id)
                disk_items.append({
                    "name": f"{disk.brand.name} {disk.model_name} {disk.width}x{disk.diameter}",
                    "article": disk.article,
                    "price": disk.price,
                    "quantity": qty,
                    "total": disk.price * qty,
                })
            except Disk.DoesNotExist:
                pass

        all_items = tire_items + disk_items

        if not all_items:
            return JsonResponse({"success": False, "error": "Кошик порожній"})

        # Calculate total
        order_total = sum(item["total"] for item in all_items)

        # Generate order number
        order_number = datetime.now().strftime("%Y%m%d%H%M%S")

        # Build items list for email
        items_text = ""
        for i, item in enumerate(all_items, 1):
            items_text += f"{i}. {item['name']}\n"
            items_text += f"   Артикул: {item['article']}\n"
            items_text += f"   Ціна: {item['price']:.0f} ₴ x {item['quantity']} шт = {item['total']:.0f} ₴\n\n"

        # Delivery method text
        delivery_methods = {
            "nova_poshta": "Нова Пошта",
            "pickup": "Самовивіз (м. Хмельницький)",
            "delivery": "Доставка по місту",
        }
        delivery_text = delivery_methods.get(delivery, delivery)

        # Prepare email
        subject = f"Нове замовлення #{order_number} - КМ/Ч 120"
        message = f"""
{'='*50}
НОВЕ ЗАМОВЛЕННЯ #{order_number}
{'='*50}

КОНТАКТНІ ДАНІ:
- Ім'я: {name}
- Телефон: {phone}
- Email: {email if email else "Не вказано"}

ДОСТАВКА:
- Спосіб: {delivery_text}
- Місто: {city if city else "Не вказано"}
- Адреса: {address if address else "Не вказано"}

{'='*50}
ТОВАРИ:
{'='*50}
{items_text}
{'='*50}
РАЗОМ ДО СПЛАТИ: {order_total:.0f} ₴
{'='*50}

Коментар: {comment if comment else "Без коментаря"}

---
Замовлення з сайту 120.com.ua
        """

        # Send email to shop
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['info@120.com.ua'],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email to shop error: {e}")

        # Send confirmation email to customer (if email provided)
        if email:
            customer_subject = f"Ваше замовлення #{order_number} - КМ/Ч 120"
            customer_message = f"""
Дякуємо за замовлення в інтернет-магазині КМ/Ч 120!

Номер замовлення: #{order_number}

ВАШЕ ЗАМОВЛЕННЯ:
{items_text}
РАЗОМ: {order_total:.0f} ₴

Спосіб доставки: {delivery_text}

Наш менеджер зв'яжеться з вами найближчим часом для підтвердження замовлення.

Контакти:
Телефон: +38 (097) 123-45-67
Сайт: https://120.com.ua

З повагою,
Команда КМ/Ч 120
            """
            try:
                send_mail(
                    subject=customer_subject,
                    message=customer_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email to customer error: {e}")

        # Clear cart after successful order
        request.session["cart"] = {"tires": {}, "disks": {}}
        request.session.modified = True

        return JsonResponse({
            "success": True,
            "message": f"Замовлення #{order_number} успішно оформлено!",
            "order_number": order_number,
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# ─── Live Chat ─────────────────────────────────────────

@require_POST
def chat_send(request):
    """Handle visitor chat message (AJAX)."""
    from . import telegram_bot

    try:
        data = json.loads(request.body)
        text = data.get("text", "").strip()
        name = data.get("name", "").strip()

        if not text:
            return JsonResponse({"success": False, "error": "Порожнє повідомлення"})

        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key
        chat_session, created = ChatSession.objects.get_or_create(
            session_key=session_key,
            defaults={"visitor_name": name, "is_active": True},
        )

        if name and chat_session.visitor_name != name:
            chat_session.visitor_name = name
            chat_session.save(update_fields=["visitor_name"])

        msg = ChatMessage.objects.create(
            session=chat_session,
            sender=ChatMessage.SENDER_VISITOR,
            text=text,
        )

        telegram_bot.send_to_admin(chat_session, text)

        return JsonResponse({
            "success": True,
            "message": {
                "id": msg.id,
                "sender": msg.sender,
                "text": msg.text,
                "created_at": msg.created_at.isoformat(),
            },
        })
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


def chat_messages(request):
    """Return chat messages for current session (AJAX, polling)."""
    if not request.session.session_key:
        return JsonResponse({"messages": []})

    try:
        chat_session = ChatSession.objects.get(session_key=request.session.session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({"messages": []})

    after = request.GET.get("after")
    qs = chat_session.messages.all()
    if after:
        qs = qs.filter(id__gt=after)

    messages = [
        {
            "id": m.id,
            "sender": m.sender,
            "text": m.text,
            "created_at": m.created_at.isoformat(),
        }
        for m in qs
    ]
    return JsonResponse({"messages": messages})


@csrf_exempt
@require_POST
def chat_telegram_webhook(request):
    """Handle incoming Telegram webhook (admin replies)."""
    import logging
    logger = logging.getLogger("catalog")

    try:
        payload = json.loads(request.body)
        logger.warning("Webhook received: %s", json.dumps(payload, ensure_ascii=False)[:500])

        message = payload.get("message", {})

        reply = message.get("reply_to_message")
        if not reply:
            logger.warning("Webhook: no reply_to_message")
            return JsonResponse({"ok": True})

        reply_message_id = reply.get("message_id")
        text = message.get("text", "").strip()
        logger.warning("Webhook: reply_to=%s, text=%s", reply_message_id, text)

        if not text or not reply_message_id:
            return JsonResponse({"ok": True})

        import re
        chat_session = None
        try:
            chat_session = ChatSession.objects.get(telegram_message_id=reply_message_id)
            logger.warning("Webhook: found session by tg_msg_id #%s", chat_session.id)
        except ChatSession.DoesNotExist:
            # Try to find session by "Сесія #N" in bot message text
            reply_text = reply.get("text", "")
            match = re.search(r"Сесія #(\d+)", reply_text)
            if match:
                try:
                    chat_session = ChatSession.objects.get(id=int(match.group(1)))
                    logger.warning("Webhook: found session by text #%s", chat_session.id)
                except ChatSession.DoesNotExist:
                    pass

        if not chat_session:
            logger.warning("Webhook: no session for tg_msg_id=%s", reply_message_id)
            return JsonResponse({"ok": True})

        ChatMessage.objects.create(
            session=chat_session,
            sender=ChatMessage.SENDER_ADMIN,
            text=text,
        )
        logger.warning("Webhook: admin message saved")

        return JsonResponse({"ok": True})
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning("Webhook error: %s", e)
        return JsonResponse({"ok": True})
