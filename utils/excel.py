import os

from openpyxl import Workbook


def save_to_excel(codes):
    wb = Workbook()
    ws = wb.active

    for i, item in enumerate(codes):
        ws.cell(row=i + 1, column=1, value=item)

    file_name = 'codes.xlsx'
    if os.path.isfile(file_name):
        i = 1
        while os.path.isfile(f'{os.path.splitext(file_name)[0]} ({i}).xlsx'):
            i += 1
        file_name = f'{os.path.splitext(file_name)[0]} ({i}).xlsx'
    wb.save(file_name)
