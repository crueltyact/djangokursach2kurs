"""
В этом модуле происходит вызов модулей парсинга для получения данных об учебных дисциплинах, затем происходит
генерация файлов РПД в формате .docx
"""

from difflib import SequenceMatcher

from docxtpl import DocxTemplate

from tkinter import filedialog
from tkinter import *
import os

from parser_matrix import get_info_from_excel
from parser_plane import get_info_from_education_plane

# Создание графического окна
gui_win = Tk()


def check_number(num: int) -> str:
    """
    Функция для проверки принадлежности числа к одной из трёх групп

    :param num: число, которое будет проверяться
    :type num: int
    :return: Возвращает одну из трёх групп
    :rtype: str
    """
    if num % 10 == 1 and num != 11:
        return '1'
    elif 1 < num % 10 < 5 and (num > 19 or num < 5):
        return '2'
    else:
        return '3'


def main() -> None:
    """
    Основная функция с циклом для графического интерфейса
    """
    gui_win.title('Генератор РПД')
    gui_win.geometry('400x200')
    gui_win.grid_rowconfigure(0, weight=1)
    gui_win.grid_columnconfigure(0, weight=1)
    dialog_btn = Button(gui_win, text='Выберите директорию для генерации РПД', command=generator)
    dialog_btn.pack()
    gui_win.mainloop()


def get_filepath() -> str:
    """
    Функция для создания дилогового окна выбора директории

    :return: строка выбранного пользователем пути
    :rtype: str
    """
    filepath = filedialog.askdirectory(initialdir=r"C:/",
                                       title="Dialog box")
    label_path = Label(gui_win, text="Генерация выполнена по пути " + filepath, font='italic 14')
    label_path.pack(pady=20)
    return filepath


def create_folder(filepath: str) -> None:
    """
    Функция для создания директории, в которую будут сохраняться файлы

    :param filepath: путь, выбранный пользователемдля генерации
    :type filepath: str
    :raises FileExistsError: если в выбранной директории уже существует папка с
    названием generated_files, программа вызовет ошибку, но продолжит работу
    """
    try:
        os.mkdir(os.path.join(filepath, "generated_files"))
    except FileExistsError:
        print("Folder already created")


def set_generator_params(data: dict, key: str) -> dict:
    """
    Функция получения информации о дисциплине по названию

    :param data: данные об учебном плане
    :type data: dict
    :param key: название учебной дисциплины
    :type key: str
    :raises KeyError: если в учебном плане не была найдена переданная учебная дисциплина
    :return: список данных о конкреной учебной дисциплине
    :rtype: dict
    """
    context_plane = {}
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
        context_plane['courses'][i]['ZET_check'] = check_number(int(context_plane['courses'][i]['ZET']))
        context_plane['courses'][i]['hours_check'] = check_number(int(context_plane['courses'][i]['hours']))
        context_plane['courses'][i]['homework_time_check'] = check_number(
            int(context_plane['courses'][i]['homework_time']))
    return context_plane


def fix_docx_tables(doc: DocxTemplate) -> None:
    """
    Функция удаления пустых строк из таблиц в генерируемом файле

    :param doc: объект генерируемого файлы
    :type doc: DocxTemplate
    """
    for i in range(len(doc.tables)):
        table = doc.tables[i]._tbl
        for row in doc.tables[i].rows:
            if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
                table.remove(row._tr)


def generate_docx(data: dict, key: str, filepath: str) -> None:
    """
    Функция генерации и сохранения файла РПД

    :param data: данные учебного плана по всем дисциплинам
    :type data: dict
    :param key: название учебной дисциплины, по которой генерируется РПД
    :type key: str
    :param filepath: путь сохранения файла, выбранный пользователем
    :type filepath: str
    """
    context_plane = set_generator_params(data, key)
    doc = DocxTemplate("../templates/template.docx")
    doc.render(dict(data[key], **context_plane))
    fix_docx_tables(doc)
    doc.save("{}/generated_files/{}.docx".format(filepath, key))


def generator() -> None:
    """
    Функция для парсинга и генерации РПД по всем учебным дисциплинам
    """
    filepath = get_filepath()
    create_folder(filepath)
    data, key_data = get_info_from_excel(
        "../media/excel/matrices/09_03_01_Информатика_и_ВТ,_Матрица_ВЕБ_технологии_2020.xlsx")
    for key in key_data:
        generate_docx(data, key, filepath)


if __name__ == '__main__':
    main()
