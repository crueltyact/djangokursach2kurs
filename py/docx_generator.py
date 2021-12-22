from docxtpl import DocxTemplate

from py.parse_plane import get_info_from_education_plane
from py.parser import get_info_from_excel


def check_number(num):
    if num % 10 == 1 and num != 11:
        return '1'
    elif 1 < num % 10 < 5 and (num > 19 or num < 5):
        return '2'
    else:
        return '3'


def main():
    contexts = get_info_from_excel("../templates/09_03_01_Информатика_и_ВТ,_Матрица_ВЕБ_технологии_2020.xlsx")
    for key in contexts:
        try:
            context_lesson = contexts[key]
            context_plane = get_info_from_education_plane("../templates/03-5190 - ВЕБ 2020 (1).xlsx")[key]
            context_plane['intensity_ZET_check'] = check_number(context_plane['intensity_ZET'])
            context_plane['intensity_hours_check'] = check_number(context_plane['intensity_hours'])
            try:
                context_plane['total_homework_hours_check'] = check_number(context_plane['total_homework_hours'])
            except Exception as e:
                print(e)
                context_plane['total_homework_hours_check'] = 0
            try:
                for i, _ in enumerate(context_plane['semesters']):
                    context_plane['semesters'][i]['ZET_check'] = check_number(context_plane['semesters'][i]['ZET'])
                    context_plane['semesters'][i]['hours_check'] = check_number(context_plane['semesters'][i]['hours'])
                    context_plane['semesters'][i]['homework_time_check'] = check_number(
                        context_plane['semesters'][i]['homework_time'])
            except Exception as e:
                print(e)
            doc = DocxTemplate("../templates/template.docx")
            doc.render(dict(context_lesson, **context_plane))
            for i in range(len(doc.tables)):
                table = doc.tables[i]._tbl
                for row in doc.tables[i].rows:
                    if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
                        table.remove(row._tr)
            doc.save("../generated_files/{}.docx".format(key))
        except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
