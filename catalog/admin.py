from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import Brand, Tire, Disk, Supplier

import json
import uuid
import threading
import tempfile
import os


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
        "studded",
        "purchase_price",
        "price",
        "in_stock",
        "is_featured",
        "supplier",
    ]
    list_filter = ["brand", "season", "studded", "in_stock", "is_featured", "diameter", "supplier"]
    search_fields = ["model_name", "article", "brand__name"]
    prepopulated_fields = {"slug": ("model_name",)}
    list_editable = ["price", "is_featured", "studded"]
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
        "is_featured",
        "supplier",
    ]
    list_filter = ["brand", "disk_type", "in_stock", "is_featured", "diameter", "bolts", "supplier"]
    search_fields = ["model_name", "article", "brand__name"]
    prepopulated_fields = {"slug": ("model_name",)}
    list_editable = ["price", "is_featured"]
    raw_id_fields = ["supplier"]


# Custom Admin Site with import functionality
class CatalogAdminSite(admin.AdminSite):
    site_header = "КМ/Ч 120 - Адміністрування"
    site_title = "КМ/Ч 120 Admin"
    index_title = "Панель управління"

    ACTIVE_IMPORT_FILE = '/tmp/import_active_task.txt'

    def _get_active_task_id(self):
        try:
            with open(self.ACTIVE_IMPORT_FILE, 'r') as f:
                task_id = f.read().strip()
            # Verify progress file still exists (import is actually running)
            if task_id and os.path.exists(self._get_progress_file(task_id)):
                return task_id
            # Stale lock file — clean up
            try:
                os.unlink(self.ACTIVE_IMPORT_FILE)
            except OSError:
                pass
        except FileNotFoundError:
            pass
        return None

    def _set_active_task_id(self, task_id):
        with open(self.ACTIVE_IMPORT_FILE, 'w') as f:
            f.write(task_id)

    def _clear_active_task_id(self):
        try:
            os.unlink(self.ACTIVE_IMPORT_FILE)
        except OSError:
            pass

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-prices/', self.admin_view(self.import_prices_view), name='import_prices'),
            path('import-prices/start/', self.admin_view(self.start_import_view), name='start_import'),
            path('import-progress/<str:task_id>/', self.admin_view(self.import_progress_view), name='import_progress'),
            path('error-logs/', self.admin_view(self.error_logs_view), name='error_logs'),
            path('recalculate-all-prices/', self.admin_view(self.recalculate_all_prices_view), name='recalculate_all_prices'),
            path('xml-feeds/', self.admin_view(self.xml_feeds_view), name='xml_feeds'),
        ]
        return custom_urls + urls

    def _get_progress_file(self, task_id):
        return f'/tmp/import_progress_{task_id}.json'

    def _write_progress(self, task_id, data):
        progress_file = self._get_progress_file(task_id)
        tmp_file = progress_file + '.tmp'
        with open(tmp_file, 'w') as f:
            json.dump(data, f)
        os.replace(tmp_file, progress_file)

    def _run_import(self, task_id, file_path, import_type):
        import django
        django.setup()
        from .import_service import import_tires, import_disks

        def progress_callback(info):
            self._write_progress(task_id, {
                'status': 'running',
                'current': info['current'],
                'total': info['total'],
                'created': info['created'],
                'updated': info['updated'],
                'skipped': info['skipped'],
                'errors_count': info['errors_count'],
                'message': f"Обробка рядка {info['current']} з {info['total']}...",
            })

        try:
            if import_type == 'tires':
                result = import_tires(file_path, progress_callback=progress_callback)
            else:
                result = import_disks(file_path, progress_callback=progress_callback)

            self._write_progress(task_id, {
                'status': 'completed',
                'current': result['total_rows'],
                'total': result['total_rows'],
                'created': result['created'],
                'updated': result['updated'],
                'skipped': result['skipped'],
                'errors_count': len(result['errors']),
                'errors': result['errors'],
                'message': 'Імпорт завершено!',
            })
        except Exception as e:
            self._write_progress(task_id, {
                'status': 'error',
                'message': f'Помилка імпорту: {str(e)}',
                'current': 0,
                'total': 0,
                'created': 0,
                'updated': 0,
                'skipped': 0,
                'errors_count': 1,
                'errors': [str(e)],
            })
        finally:
            try:
                os.unlink(file_path)
            except OSError:
                pass
            self._clear_active_task_id()

    def import_prices_view(self, request):
        context = {
            'tire_count': Tire.objects.count(),
            'disk_count': Disk.objects.count(),
            'brand_count': Brand.objects.count(),
            'supplier_count': Supplier.objects.count(),
            'active_task_id': self._get_active_task_id() or '',
        }
        return render(request, 'admin/catalog/import_prices.html', context)

    def start_import_view(self, request):
        if request.method != 'POST':
            return JsonResponse({'error': 'POST only'}, status=405)

        if self._get_active_task_id():
            return JsonResponse({
                'error': 'Імпорт вже виконується. Дочекайтесь завершення.'
            }, status=409)

        import_type = request.POST.get('import_type')
        excel_file = request.FILES.get('excel_file')

        if not excel_file:
            return JsonResponse({'error': 'Будь ласка, виберіть файл'}, status=400)

        if import_type not in ('tires', 'disks'):
            return JsonResponse({'error': 'Невірний тип імпорту'}, status=400)

        # Save uploaded file
        suffix = '.xlsx' if excel_file.name.endswith('.xlsx') else '.xls'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in excel_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        task_id = str(uuid.uuid4())

        # Write initial progress
        self._write_progress(task_id, {
            'status': 'running',
            'current': 0,
            'total': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors_count': 0,
            'message': 'Читання файлу...',
        })

        self._set_active_task_id(task_id)

        thread = threading.Thread(
            target=self._run_import,
            args=(task_id, tmp_path, import_type),
            daemon=True,
        )
        thread.start()

        return JsonResponse({'task_id': task_id})

    def import_progress_view(self, request, task_id):
        progress_file = self._get_progress_file(task_id)
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
            # Clean up progress file after client gets final status
            if data.get('status') in ('completed', 'error'):
                try:
                    os.unlink(progress_file)
                except OSError:
                    pass
                self._clear_active_task_id()
            return JsonResponse(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return JsonResponse({'status': 'unknown', 'message': 'Завдання не знайдено'}, status=404)

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
