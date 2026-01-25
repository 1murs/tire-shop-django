from django.core.paginator import Paginator
from django.shortcuts import render
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
    Shows featured tires (first 3 in stock).
    """
    featured_tires = Tire.objects.filter(in_stock=True)[:3]

    context = {
        "featured_tires": featured_tires,
    }
    return render(request, "catalog/index.html", context)


def tire_list(request):
    """List of all tires with pagination."""
    tires_all = Tire.objects.all()
    paginator = Paginator(tires_all, 15)
    page_number = request.GET.get("page")
    tires = paginator.get_page(page_number)

    context = {
        "tires": tires,
    }
    return render(request, "catalog/tire_list.html", context)


def disk_list(request):
    """List of all disks with pagination."""

    disks_all = Disk.objects.all()
    paginator = Paginator(disks_all, 15)
    page_number = request.GET.get("page")
    disks = paginator.get_page(page_number)

    context = {
        "disks": disks,
    }
    return render(request, "catalog/disk_list.html", context)
