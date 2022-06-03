from future.backports.datetime import datetime
from openpyxl import load_workbook

from utils.core import get_templates_folder, get_media_folder
from utils.data_processing import get_archive_data, get_trading_table
from web.context_pro import _
from web.models import Product


def export_archive_data(start_date=None, end_date=None, waiter=None, order_type=None):
    archive_info = get_archive_data(start_date, end_date, waiter, order_type)
    trading_info, __, ___ = get_trading_table(start_date=start_date, end_date=end_date, order_type=order_type)
    stock_info = Product.objects.all()
    wb = load_workbook(get_templates_folder() + "\\excel\\archive.xlsx")
    tp = {
        'table': "Shu yerda",
        'pickup': "Olib ketilgan"
    }
    sheet = wb.worksheets[0]
    trading_sheet = wb.worksheets[1]
    stock_sheet = wb.worksheets[2]

    sheet['B1'] = _('ex_1')
    sheet['H1'] = _('ex_2')
    sheet['K1'] = _('ex_3')
    sheet['L1'] = _('ex_4')
    sheet['O1'] = _('ex_5')
    sheet['B2'] = _('ex_6')
    sheet['C2'] = _('ex_7')
    sheet['D2'] = _('ex_8')
    sheet['E2'] = _('ex_9')
    sheet['F2'] = _('ex_10')
    sheet['G2'] = _('ex_11')
    sheet['H2'] = _('ex_12')
    sheet['I2'] = _('ex_13')
    sheet['J2'] = _('ex_14')
    sheet['L2'] = _('ex_15')
    sheet['M2'] = _('ex_16')
    sheet['N2'] = _('ex_17')
    trading_sheet['B1'] = _('ex_18')
    trading_sheet['C1'] = _('ex_19')
    trading_sheet['D1'] = _('ex_20')
    trading_sheet['E1'] = _('ex_201')
    stock_sheet['B1'] = _('ex_19')
    stock_sheet['C1'] = _('ex_21')
    stock_sheet['D1'] = _('ex_22')
    stock_sheet['E1'] = _('ex_23')

    c = 1
    for order in archive_info.orders:
        if not order.table:
            table = ""
            room = ""
        else:
            table = order.table.number
            room = order.table.room.title
        sheet.append([c, order.id, order.waiter.full_name, tp[order.order_type], order.created_time, room, table,
                      order.waiter_fee, order.room_service_cost, order.without_tax, order.needed_payment,
                      order.cash_money, order.credit_card, order.debt_money, order.paid_money])
        c += 1
    c = 1
    for food_type in trading_info:
        trading_sheet.append([c, food_type.category.title, food_type.title, food_type.total_sold, food_type.total_sale])
        c += 1
    c = 1
    for product in stock_info:
        stock_sheet.append([c, product.title, product.price, product.quantity, product.last_added_time_formatted])
    file_name = datetime.now().strftime('archive_report_%d_%m_%Y_%H_%M_%S.xlsx')
    wb.save(f"{get_media_folder()}\\reports\\{file_name}")
    return f"/media/reports/{file_name}"
