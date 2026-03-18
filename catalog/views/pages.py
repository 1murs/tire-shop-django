from django.shortcuts import render


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
