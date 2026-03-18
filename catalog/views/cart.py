import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from ..models import Tire, Disk


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
