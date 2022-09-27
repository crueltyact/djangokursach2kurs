from difflib import SequenceMatcher

from docxtpl import DocxTemplate

from tkinter import filedialog
from tkinter import *
import os

from excel_to_doc_parser.py.parser import get_info_from_excel
from excel_to_doc_parser.py.parser_plane import get_info_from_education_plane


def check_number(num):
    if num % 10 == 1 and num != 11:
        return '1'
    elif 1 < num % 10 < 5 and (num > 19 or num < 5):
        return '2'
    else:
        return '3'


gui_win = Tk()


def main():
    gui_win.title('Генератор РПД')
    gui_win.geometry('400x200')
    gui_win.grid_rowconfigure(0, weight=1)
    gui_win.grid_columnconfigure(0, weight=1)
    dialog_btn = Button(gui_win, text='Выберите директорию для генерации РПД', command=generator)
    dialog_btn.pack()
    gui_win.mainloop()


def generator():
    filepath = filedialog.askdirectory(initialdir=r"C:/",
                                       title="Dialog box")
    label_path = Label(gui_win, text="Генерация выполнена по пути " + filepath, font='italic 14')
    label_path.pack(pady=20)
    try:
        os.mkdir(os.path.join(filepath, "generated_files"))
    except FileExistsError:
        print("Folder already created")
    data, key_data = get_info_from_excel(
        "../media/excel/matrices/09_03_01_Информатика_и_ВТ,_Матрица_ВЕБ_технологии_2020.xlsx")
    for key in key_data:
        try:
            context_plane = get_info_from_education_plane("../media/excel/planes/03-5190 - ВЕБ 2020 (1).xlsx")[key]
        except KeyError:
            for error_key in get_info_from_education_plane("../media/excel/planes/03-5190 - ВЕБ 2020 (1).xlsx"):
                if SequenceMatcher(None, key, error_key).ratio() >= 0.75:
                    context_plane = get_info_from_education_plane("../media/excel/planes/03-5190 - ВЕБ 2020 (1).xlsx")[
                        error_key]
                    break
        context_plane["program_name"] = data[key]["program_name"]
        context_plane["program_code"] = data[key]["program_code"]
        context_plane["profile_name"] = data[key]["profile_name"]
        context_plane["year_start"] = data[key]["year_start"]
        context_plane["current_year"] = data[key]["current_year"]
        context_plane['intensity_ZET_check'] = check_number(context_plane['intensity_ZET'])
        context_plane['intensity_hours_check'] = check_number(context_plane['intensity_hours'])
        context_plane['total_homework_hours_check'] = check_number(context_plane['total_homework_hours'])
        for i, _ in enumerate(context_plane['courses']):
            context_plane['courses'][i]['ZET_check'] = check_number(context_plane['courses'][i]['ZET'])
            context_plane['courses'][i]['hours_check'] = check_number(context_plane['courses'][i]['hours'])
            context_plane['courses'][i]['homework_time_check'] = check_number(
                context_plane['courses'][i]['homework_time'])
        doc = DocxTemplate("../templates/template.docx")
        doc.render(dict(data[key], **context_plane))
        for i in range(len(doc.tables)):
            table = doc.tables[i]._tbl
            for row in doc.tables[i].rows:
                if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
                    table.remove(row._tr)
        doc.save("{}/generated_files/{}.docx".format(filepath, key))


if __name__ == '__main__':
    main()
