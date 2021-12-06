from docxtpl import DocxTemplate

from py.parser import get_info_from_excel


def main():
    contexts = get_info_from_excel("../templates/09_03_01_Информатика_и_ВТ,_Матрица_ВЕБ_технологии_2020.xlsx")
    for key in contexts:
        doc = DocxTemplate("../templates/template.docx")
        doc.render(contexts[key])
        for i in range(len(doc.tables)):
            table = doc.tables[i]._tbl
            for row in doc.tables[i].rows:
                if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
                    table.remove(row._tr)
        doc.save("../generated_files/{}.docx".format(contexts[key]['program_name']))


if __name__ == '__main__':
    main()
