from future.backports.datetime import datetime
from openpyxl import load_workbook

from utils.core import get_templates_folder, get_media_folder
from utils.data_processing import get_archive_data


def export_archive_data(start_date=None, end_date=None, waiter=None, order_type=None):
    archive_info = get_archive_data(start_date, end_date, waiter, order_type)
    wb = load_workbook(get_templates_folder() + "\\archive.xlsx")
    tp = {
        'table': "Shu yerda",
        'pickup': "Olib ketilgan"
    }
    sheet = wb.active
    c = 1
    for order in archive_info.orders:
        sheet.append([c, order.id, order.waiter.full_name, tp[order.order_type], order.created_time, order.table.room.title, order.table.number, order.waiter_fee, order.room_service_cost, order.without_tax, order.needed_payment, order.cash_money, order.credit_card, order.debt_money, order.paid_money])
        c += 1
    file_name = datetime.now().strftime('archive_report_%d/%m/%Y_%H_%M_%S')
    wb.save(f"\\{get_media_folder()}\\reports\\{file_name}")
    return f"/media/reports/{file_name}"

