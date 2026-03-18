from django.http import JsonResponse
from django.shortcuts import render

from ..models import CarFitment


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
