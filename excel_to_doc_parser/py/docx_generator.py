from difflib import SequenceMatcher

import numpy
import pandas as pd
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


# gui_win = Tk()


def main():
    # with open('../../../pdfParser/17918 09.03.01 СПИ ОФО 2022+.pdf', 'rb') as pdf:
    #     pdfReader = PyPDF2.PdfFileReader(pdf)
    #     print(pdfReader.numPages)
    #     pageObj = pdfReader.getPage(0)
    #     count = 0
    #     for image_file_object in pageObj.images:
    #         with open(str(count) + image_file_object.name, "wb") as fp:
    #             fp.write(image_file_object.data)
    #             count += 1

    # generator()
    data = parse_plane("../media/excel/planes/17921 09.03.03 ИТУБ ОФО 2022 (3).xlsx")["Основные дисциплины"]
    header = get_header("../media/excel/planes/03-5190 - ВЕБ 2020 (1).xlsx")
    disciplines_with_course_project = []
    for index, row in data[header["Экзамены"]].items():
        if not pd.isna(row):
            disciplines_with_course_project.append(data.iloc[index - 1].iloc[header["Название дисциплины"] - 1])
    print(disciplines_with_course_project)
    # gui_win.title('Генератор РПД')
    # gui_win.geometry('400x200')
    # gui_win.grid_rowconfigure(0, weight=1)
    # gui_win.grid_columnconfigure(0, weight=1)
    # dialog_btn = Button(gui_win, text='Выберите директорию для генерации РПД', command=generator)
    # dialog_btn.pack()
    # gui_win.mainloop()


def get_sem(data, index):
    context = {}
    for i, key in enumerate(data.iloc[:, index:].values[1], index + 1):
        if not pd.isna(key):
            context[key] = i
        else:
            break
    return context


def get_hours(data, index):
    context = {}
    for i, key in enumerate(data.iloc[:, index:].values[1], index + 1):
        if not pd.isna(key) and "курс" not in key:
            context[key] = i
        else:
            break
    return context


def get_courses(data, index):
    context = {}
    for i, key in enumerate(data.iloc[:, index:].values[2], index + 1):
        if not pd.isna(key) and "курс" not in key:
            context[key] = i
        else:
            break
    return context


def get_header(filename):
    header = {}
    df = pd.read_excel(filename, header=None, index_col=None)
    data = df.dropna(axis="columns", how="all")
    disciplines = data.copy()
    header_row = disciplines[disciplines.loc[disciplines[2] == "Шифр"].head().index[0]: disciplines.loc[disciplines[2] == "Шифр"].head().index[0] + 3].dropna(axis="columns", how='all')
    header_row.columns = pd.RangeIndex(header_row.columns.size)
    for i, key in enumerate(header_row.values[0], 1):
        if not pd.isna(key):
            if "распределение по семестрам" in key.lower():
                header = dict(**header, **get_sem(header_row, i - 1))
            elif "часы" in key.lower():
                header = dict(**header, **get_hours(header_row, i - 1))
            elif "распределение по курсам" in key.lower():
                header = dict(**header, **get_courses(header_row, i - 1))
            else:
                header[key] = i
    return header


def parse_plane(filename):
    context = {}
    df = pd.read_excel(filename, header=None, index_col=None)
    # with open("columns.json", "w", encoding='utf-8') as f:
    #     json.dump(df.to_dict(), f, ensure_ascii=False)
    data = df.dropna(axis="columns", how="all")
    disciplines = data.copy()
    start_index = 0
    for index, column in disciplines.items():
        if "Блок 1. Дисциплины (модули)" in numpy.array2string(column.values):
            start_index = index
    disciplines = disciplines.drop(range(data.loc[data[start_index] == "Блок 1. Дисциплины (модули)"].head().index[0] - 1))
    context["Факультативные дисциплины"] = data[3].iloc[
        range(data.loc[data[2].isin(["№ п/п"])].head().index[0], data.iloc[-1:].head().index[0] + 1)]
    disciplines = disciplines.drop(
        range(data.loc[data[2].isin(["№ п/п"])].head().index[0], data.iloc[-1:].head().index[0] + 1))
    for column in data:
        if data[column].isin(["8 семестр\n6 недель"]).any():
            break
    disciplines = disciplines.iloc[:, range(column - 1)]
    disciplines = disciplines.dropna(axis='columns', how="all").dropna(axis="rows", how="all")
    # context["Факультативные дисциплины"] = context["Факультативные дисциплины"].dropna(axis='columns', how='all').dropna(axiss='rows', how='all')
    disciplines.reset_index(drop=True, inplace=True)
    new_header = disciplines.iloc[0].astype(int)
    disciplines = disciplines[1:]
    disciplines.columns = new_header
    context["Основные дисциплины"] = disciplines
    return context


def generator():
    # filepath = filedialog.askdirectory(initialdir=r"C:/",
    #                                    title="Dialog box")
    # label_path = Label(gui_win, text="Генерация выполнена по пути " + filepath, font='italic 14')
    # label_path.pack(pady=20)
    # try:
    #     os.mkdir(os.path.join(filepath, "generated_files"))
    # except FileExistsError:
    #     print("Folder already created")
    context_plane = {}
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
        doc.save("../../generated_files/{}.docx".format(key))


if __name__ == '__main__':
    main()
