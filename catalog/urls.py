from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.index, name="index"),
    path("tires/", views.tire_list, name="tire_list"),
    path("disks/", views.disk_list, name="disk_list"),
]
