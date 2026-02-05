from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Brand, Tire, Disk, Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "is_preorder", "markup_percent", "delivery_days", "is_active", "product_count"]
    list_filter = ["is_preorder", "is_active"]
    search_fields = ["name", "code"]
    list_editable = ["markup_percent", "delivery_days", "is_active"]
    ordering = ["name"]
    actions = ["recalculate_prices"]

    fieldsets = (
        ("Основна інформація", {
            "fields": ("name", "code", "is_active")
        }),
        ("Налаштування наявності", {
            "fields": ("is_preorder", "delivery_days"),
            "description": "Постачальники з '21 день' в назві автоматично = 'Під замовлення'"
        }),
        ("Націнка", {
            "fields": ("markup_percent",),
            "description": "Націнка застосовується до закупівельної ціни. Після зміни натисніть 'Перерахувати ціни'"
        }),
    )

    def product_count(self, obj):
        tires = obj.tires.count()
        disks = obj.disks.count()
        return f"{tires} шин, {disks} дисків"
    product_count.short_description = "Товарів"

    @admin.action(description="Перерахувати ціни для обраних постачальників")
    def recalculate_prices(self, request, queryset):
        from .import_service import recalculate_prices_for_supplier

        total_tires = 0
        total_disks = 0

        for supplier in queryset:
            tires, disks = recalculate_prices_for_supplier(supplier)
            total_tires += tires
            total_disks += disks

        self.message_user(
            request,
            f"Ціни перераховано: {total_tires} шин, {total_disks} дисків",
            messages.SUCCESS
        )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(Tire)
class TireAdmin(admin.ModelAdmin):
    list_display = [
        "article",
        "brand",
        "model_name",
        "width",
        "profile",
        "diameter",
        "season",
        "purchase_price",
        "price",
        "in_stock",
        "supplier",
    ]
    list_filter = ["brand", "season", "in_stock", "diameter", "supplier"]
    search_fields = ["model_name", "article", "brand__name"]
    prepopulated_fields = {"slug": ("model_name",)}
    list_editable = ["price"]
    raw_id_fields = ["supplier"]


@admin.register(Disk)
class DiskAdmin(admin.ModelAdmin):
    list_display = [
        "article",
        "brand",
        "model_name",
        "diameter",
        "width",
        "bolts",
        "pcd",
        "et",
        "disk_type",
        "purchase_price",
        "price",
        "in_stock",
        "supplier",
    ]
    list_filter = ["brand", "disk_type", "in_stock", "diameter", "bolts", "supplier"]
    search_fields = ["model_name", "article", "brand__name"]
    prepopulated_fields = {"slug": ("model_name",)}
    list_editable = ["price"]
    raw_id_fields = ["supplier"]


# Custom Admin Site with import functionality
class CatalogAdminSite(admin.AdminSite):
    site_header = "КМ/Ч 120 - Адміністрування"
    site_title = "КМ/Ч 120 Admin"
    index_title = "Панель управління"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-prices/', self.admin_view(self.import_prices_view), name='import_prices'),
            path('error-logs/', self.admin_view(self.error_logs_view), name='error_logs'),
            path('recalculate-all-prices/', self.admin_view(self.recalculate_all_prices_view), name='recalculate_all_prices'),
            path('xml-feeds/', self.admin_view(self.xml_feeds_view), name='xml_feeds'),
        ]
        return custom_urls + urls

    def import_prices_view(self, request):
        from .import_service import import_tires, import_disks
        import tempfile
        import os

        context = {
            'tire_count': Tire.objects.count(),
            'disk_count': Disk.objects.count(),
            'brand_count': Brand.objects.count(),
            'supplier_count': Supplier.objects.count(),
        }

        if request.method == 'POST':
            import_type = request.POST.get('import_type')
            excel_file = request.FILES.get('excel_file')

            if not excel_file:
                context['error'] = 'Будь ласка, виберіть файл'
            else:
                # Save uploaded file temporarily
                suffix = '.xlsx' if excel_file.name.endswith('.xlsx') else '.xls'
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    for chunk in excel_file.chunks():
                        tmp.write(chunk)
                    tmp_path = tmp.name

                try:
                    if import_type == 'tires':
                        result = import_tires(tmp_path)
                    else:
                        result = import_disks(tmp_path)
                    context['result'] = result
                    # Update counts after import
                    context['tire_count'] = Tire.objects.count()
                    context['disk_count'] = Disk.objects.count()
                    context['brand_count'] = Brand.objects.count()
                    context['supplier_count'] = Supplier.objects.count()
                except Exception as e:
                    context['error'] = f'Помилка імпорту: {str(e)}'
                finally:
                    os.unlink(tmp_path)

        return render(request, 'admin/catalog/import_prices.html', context)

    def recalculate_all_prices_view(self, request):
        from .import_service import recalculate_prices_for_supplier

        total_tires = 0
        total_disks = 0

        for supplier in Supplier.objects.filter(is_active=True):
            tires, disks = recalculate_prices_for_supplier(supplier)
            total_tires += tires
            total_disks += disks

        messages.success(request, f"Ціни перераховано: {total_tires} шин, {total_disks} дисків")
        return redirect('admin:import_prices')

    def error_logs_view(self, request):
        from django.conf import settings

        log_file = settings.BASE_DIR / "logs" / "errors.log"
        logs = ""

        if request.method == 'POST' and request.POST.get('action') == 'clear':
            # Clear logs
            if log_file.exists():
                with open(log_file, 'w') as f:
                    f.write('')

        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = f.read()
                # Show last 100 lines
                lines = logs.strip().split('\n')
                if len(lines) > 100:
                    logs = '\n'.join(lines[-100:])

        return render(request, 'admin/catalog/error_logs.html', {'logs': logs})

    def xml_feeds_view(self, request):
        base_url = request.build_absolute_uri('/').rstrip('/')
        suppliers = Supplier.objects.filter(is_active=True).order_by('name')

        return render(request, 'admin/catalog/xml_feeds.html', {
            'base_url': base_url,
            'suppliers': suppliers,
        })


# Replace default admin site
admin.site.__class__ = CatalogAdminSite
