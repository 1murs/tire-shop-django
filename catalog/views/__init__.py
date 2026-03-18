from .pages import about, delivery, pre_order, contacts
from .catalog import index, tire_list, disk_list, tire_detail, disk_detail, search
from .cart import get_cart, save_cart, cart_view, cart_add, cart_update, cart_remove, cart_count
from .orders import callback_request, one_click_order, checkout, checkout_submit
from .calculator import (
    tire_calculator, calculator_by_car, calculator_get_models,
    calculator_get_years, calculator_get_modifications, calculator_get_fitment,
)
from .chat import chat_send, chat_messages, chat_telegram_webhook
