from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from ..models import Tire, Disk, Brand


def index(request):
    """
    Home page view.
    Shows featured tires and filter options for quick search.
    """
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
