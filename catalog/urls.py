from django.urls import path, re_path
from . import views
from . import feeds

app_name = "catalog"

urlpatterns = [
    # XML feeds for price aggregators
    path("storage/e-katalog/price.xml", feeds.generate_ekatalog_xml, name="ekatalog_feed"),
    path("feed/price.xml", feeds.generate_ekatalog_xml, name="price_feed"),
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
    path("checkout/", views.checkout, name="checkout"),
    path("checkout/submit/", views.checkout_submit, name="checkout_submit"),
    path("about/", views.about, name="about"),
    path("delivery/", views.delivery, name="delivery"),
    path("pre-order/", views.pre_order, name="pre_order"),
    path("contacts/", views.contacts, name="contacts"),
    path("callback/", views.callback_request, name="callback_request"),
    path("one-click-order/", views.one_click_order, name="one_click_order"),
    # Calculators
    path("calculator/", views.tire_calculator, name="calculator"),
    path("calculator/by-car/", views.calculator_by_car, name="calculator_by_car"),
    path("calculator/models/", views.calculator_get_models, name="calculator_models"),
    path("calculator/years/", views.calculator_get_years, name="calculator_years"),
    path("calculator/modifications/", views.calculator_get_modifications, name="calculator_modifications"),
    path("calculator/fitment/", views.calculator_get_fitment, name="calculator_fitment"),
]
