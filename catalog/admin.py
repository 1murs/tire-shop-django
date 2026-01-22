from django.contrib import admin
from .models import Brand, Tire, Disk


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
        "price",
        "in_stock",
    ]
    list_filter = ["brand", "season", "in_stock", "diameter"]
    search_fields = ["model_name", "article", "brand__name"]
    prepopulated_fields = {"slug": ("model_name",)}
    list_editable = ["price", "in_stock"]


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
        "color",
        "price",
        "in_stock",
    ]
    list_filter = ["brand", "disk_type", "in_stock", "diameter", "bolts"]
    search_fields = ["model_name", "article", "brand__name"]
    prepopulated_fields = {"slug": ("model_name",)}
    list_editable = ["price", "in_stock"]
