from django.urls import path, re_path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.search, name="search"),
    path("tires/", views.tire_list, name="tire_list"),
    re_path(r"^tires/(?P<slug>[\w.-]+)/$", views.tire_detail, name="tire_detail"),
    path("disks/", views.disk_list, name="disk_list"),
    re_path(r"^disks/(?P<slug>[\w.-]+)/$", views.disk_detail, name="disk_detail"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/", views.cart_add, name="cart_add"),
    path("cart/update/", views.cart_update, name="cart_update"),
    path("cart/remove/", views.cart_remove, name="cart_remove"),
    path("cart/count/", views.cart_count, name="cart_count"),
    path("about/", views.about, name="about"),
    path("delivery/", views.delivery, name="delivery"),
    path("pre-order/", views.pre_order, name="pre_order"),
    path("contacts/", views.contacts, name="contacts"),
]
