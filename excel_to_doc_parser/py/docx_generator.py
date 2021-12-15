from docxtpl import DocxTemplate

from excel_to_doc_parser.py.parser import get_info_from_excel


def main():
    contexts = get_info_from_excel(
        "../media/excel/09_03_03_Прикладная_информатика,"
        "_Матрица_Большие_и_открытые_данные_2020.xlsx")
    for key in contexts:
        doc = DocxTemplate("../templates/template.docx")
        doc.render(contexts[key])
        for i in range(len(doc.tables)):
            table = doc.tables[i]._tbl
            for row in doc.tables[i].rows:
                if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
                    table.remove(row._tr)
        doc.save("../media/generated_files/{}.docx".format(contexts[key]['program_name']))


if __name__ == '__main__':
    main()
