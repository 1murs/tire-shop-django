import json

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from ..models import Tire, Disk
from .cart import get_cart


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
