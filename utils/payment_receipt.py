from datetime import datetime

from utils.printer import Document
from utils.system_settings import Settings
from web.models import Order


def print_receipt(order: Order):
    border_string = "-" * 200
    doc = Document(width=int(Settings().get("printer_width", int) * 51))
    doc.begin_document()
    y = 0
    doc.set_font(family="Arial", size=20, bold=True)
    company_name = Settings().get(key="company_name", tp=str)
    if company_name == "":
        company_name = "SerWibe"
    doc.aligned_text(company_name, y=y, align="center")
    y += 400
    doc.set_font(family="Arial", size=8, bold=False)
    if Settings().get("address", tp=str):
        doc.aligned_text("Manzil: " + Settings().get(key="address", tp=str), y=y, align="center")
        y += 150
    phone_number = Settings().get("phone_number", tp=str)
    if len(phone_number) != 17:
        doc.aligned_text("Tel: " + Settings().get(key="phone_number", tp=str), y=y, align="center")
        y += 150
    doc.set_font(family="Arial", size=12, bold=False)
    doc.aligned_text(border_string, y, align="center")
    y += 200
    doc.aligned_text("Sana:", y, align="left")
    doc.aligned_text(datetime.now().strftime("%d/%m/%Y, %H:%M:%S"), y, align="right")
    y += 300
    doc.aligned_text("Buyurtma raqami:", y, align="left")
    doc.aligned_text('#' + str(order.id), y, align="right")
    y += 300
    doc.aligned_text("Xona:", y, align="left")
    doc.aligned_text(str(order.table.room.title), y, align="right")
    y += 300
    doc.aligned_text("Stol raqami:", y, align="left")
    doc.aligned_text(str(order.table.number), y, align="right")
    y += 300
    doc.aligned_text("Offitsant:", y, align="left")
    doc.aligned_text(str(order.waiter.full_name), y, align="right")
    y += 200
    doc.aligned_text(border_string, y, align="center")
    y += 200
    doc.set_font(family="Arial", size=16, bold=True)
    doc.aligned_text("Buyurtmalar", y, align="center")
    doc.set_font(family="Arial", size=12, bold=False)
    y += 300
    doc.aligned_text(border_string, y, align="center")
    y += 200
    for order_item in order.orderitem_set.all():
        doc.aligned_text(f"{order_item.quantity} x {order_item.meal.title}", y, align="left")
        doc.aligned_text(f"{order_item.total_price} so'm", y, align="right")
        y += 300
    y -= 100
    doc.aligned_text(border_string, y, align="center")
    y += 200
    doc.aligned_text("Umumiy summa:", y, align="left")
    doc.aligned_text(f"{order.needed_payment} so'm", y, align="right")
    y += 300
    tax = Settings().get("tax", tp=int)
    if tax != 0:
        doc.aligned_text("Tax:", y, align="left")
        doc.aligned_text(f"{tax} %", y, align="right")
        y += 300
    doc.set_font(family="Arial", size=14, bold=True)
    doc.aligned_text("Jami:", y, align="left")
    doc.aligned_text(f"{order.needed_payment * (1 + tax / 100)} so'm", y, align="right")
    doc.set_font(family="Arial", size=12, bold=False)
    if Settings().get("last_message", tp=str):
        y += 500
        doc.aligned_text(border_string, y, align="center")
        y += 200
        doc.set_font(family="Arial", size=20, bold=True)
        doc.aligned_text(Settings().get(key="last_message", tp=str), y=y, align="center")
        doc.set_font(family="Arial", size=12, bold=False)
        y += 400
        doc.aligned_text(border_string, y, align="center")
    y += 200
    doc.set_font(family="Arial", size=8, bold=False)
    doc.aligned_text("Created by serwibe.uz", y, align="right")
    doc.end_document()
