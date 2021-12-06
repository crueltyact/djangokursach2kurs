import xlrd
import datetime


def get_part_type(matrix, c):
    i = c
    while matrix[1][i] == '':
        i -= 1
    return matrix[1][i]


# возвращает код компетенции, индикатор компетенции и текст компетенции
def get_parents(matrix, r):
    fst = ''
    scd = ''

    i = r
    while matrix[i][1] == '': i -= 1
    scd = matrix[i][1].strip().replace('\n', '')

    i = r
    while matrix[i][0] == '': i -= 1
    fst = matrix[i][0].strip().replace('\n', '')

    return [fst, scd, matrix[r][2]]


def get_info_for_table(matrix, rng, c):
    res = [
        {
            'competency_code': '',
            'competency_name': '',
            'indicators': [['', set()]]
        }
    ]

    for r in rng:
        if matrix[r][c] == ' + ':

            # ищем, к какому индикатору и коду компетенции относится найденное требование
            f_code, s_code, t_code = get_parents(matrix, r)

            code, name = [el.strip() for el in list(filter(bool, f_code.split('.')))]
            # print(f'code="{code}", name="{name}"')
            if res[-1]['competency_code'] != code:
                res.append({
                    'competency_code': code,
                    'competency_name': name,
                    'indicators': [['', set()]]
                })

                res[-1]['indicators'][0][0] = s_code
                res[-1]['indicators'][0][1].add(t_code)
            else:
                if res[-1]['indicators'][-1][0] != s_code:
                    res[-1]['indicators'].append(['', set()])
                    res[-1]['indicators'][-1][0] = s_code
                    res[-1]['indicators'][-1][1].add(t_code)
                else:
                    res[-1]['indicators'][-1][1].add(t_code)
    del res[0]
    return res


def get_ranges(matrix):
    rows = len(matrix)
    skill_types = []
    k = 0
    for i in range(rows)[1::]:
        if matrix[i][2] == '' and matrix[i + 1][2] != '':
            skill_types += [range(k, i)]
            k = i
    del skill_types[0]
    skill_types += [range(k, rows)]
    return skill_types


def parse_title(txt):
    import re
    res = {}
    txt = re.sub('[»«]', '"', txt)
    txt = re.sub('[\n,]', '', txt)
    mas = txt.split('"')
    res['profile_name'] = mas[5]
    res['program_code'] = mas[3]
    txt = re.sub('["]', ' ', txt)
    mas = txt.split()
    for el in mas:
        if el.count('.') == 2:
            res['program_code'] = el + ' ' + res['program_code']
        if el.count('/') == 1:
            temp = el.split('/')
            res['year_start'] = temp[0]
            res['year_end'] = temp[1]
    return res


def get_matrix(filename):
    xls = xlrd.open_workbook(filename)
    xls = xls.sheet_by_index(0)

    # преобразуем обьект Sheet в матрицу python
    return [
        [xls.cell_value(i, j) for j in range(xls.ncols)]
        for i in range(xls.nrows)
    ]


# главная функция
def get_info_from_excel(filename):
    # получаем python матрицу из excel файла
    matrix = get_matrix(filename)

    # удаляем пустые строки
    for i in range(len(matrix))[::-1]:
        if len(list(filter(bool, matrix[i]))) == 0: del matrix[i]

    # размеры матрицы
    rows, cols = len(matrix), len(matrix[0])

    # создаем массив диапазонов "Универсальной", "Общепрофессиональной", "Профессиональной" компетенции
    skill_types = get_ranges(matrix)

    # парсим title
    title = parse_title(matrix[0][0])

    # Главный выходной словарь
    data = {}

    # заполняем data всеми дисциплинами и их данными
    for c in range(cols)[3::]:
        key = matrix[2][c]
        data[key] = {}
        data[key]['program_name'] = key
        data[key]['profile_name'] = title['profile_name']
        data[key]['program_code'] = title['program_code']
        data[key]['year_start'] = title['year_start']
        data[key]['year_end'] = title['year_end']
        data[key]['current_year'] = str(datetime.date.today().year)
        data[key]['part_type'] = str.lower(get_part_type(matrix, c))

        # основной алгоритм заполнения данных для docx таблиц
        universal_competences = get_info_for_table(matrix, skill_types[0], c)
        general_professional_competencies = get_info_for_table(matrix, skill_types[1], c)
        professional_competencies = get_info_for_table(matrix, skill_types[2], c)

        if len(universal_competences) > 0:
            data[key]['universal_competences'] = universal_competences
        if len(general_professional_competencies) > 0:
            data[key]['general_professional_competencies'] = general_professional_competencies
        if len(professional_competencies) > 0:
            data[key]['professional_competencies'] = professional_competencies

    return data
