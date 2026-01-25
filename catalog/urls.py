from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.index, name="index"),
    path("tires/", views.tire_list, name="tire_list"),
    path("disks/", views.disk_list, name="disk_list"),
    path("about/", views.about, name="about"),
    path("delivery/", views.delivery, name="delivery"),
    path("pre-order/", views.pre_order, name="pre_order"),
    path("contacts/", views.contacts, name="contacts"),
]
