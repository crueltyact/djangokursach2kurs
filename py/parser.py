
import xlrd
import os



# Вид выходного словаря:

# {
#     'Навыки эффективной презентации' : {
#         'program_name' : 'Навыки эффективной презентации',
#         'profile_name' : 'Корпоративные информационные системы',
#         'year_start' : '2021',
#         'year_end' : '2022',
#         'program_code' : '09.03.03',
#         'part_type' : 'обязательная часть',

#         ----- данные для таблицы -----
        
#         'universal_competentions' : [
#             [
#                 'УК-3', // 1-й стлобец
#                 'Способен осуществлять социальное взаимодействие и реализовывать свою роль в команде', // 2-й стлобец
#                 [ // данные для 3-го стлобца
#                     ['УК-3.1. Знать:', [
#                         'способы социального взаимодействия',
#                         'Методологические основы принятия управленческого решения',
#                     ]],
#                     ['УК-3.2. Уметь:', [
#                         'Принимать решения с соблюдением этических принципов их реализации',
#                     ]
#                 ],
#             ]],
#         ],

#         'average_prof_competentions' : [
#             ['ОПК-3', 'Способен решать стандартные задачи ...', [
#                 ['ОПК-3.1. Знать:', [
#                     'методы и средства решения стандартных задач ...',
#                     ...
#                 ]],
#             ]],
#         ],

#         'prof_competentions' : [
#             структура аналогична 'universal_competentions'
#         ],
#     },
#
#     ...
# }




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
        ['', '', [['', []]]]
    ]

    for r in rng:
        if matrix[r][c] == ' + ':
            
            # ищем, к какому индикатору и коду компетенции относится найденное требование
            f_code, s_code, t_code = get_parents(matrix, r)
            
            code, name = [el.strip() for el in list(filter(bool, f_code.split('.')))]
            # print(f'code="{code}", name="{name}"')
            if res[-1][0] != code:
                res.append(['', '', [['', []]]])
                res[-1][0] = code
                res[-1][1] = name
                res[-1][2][0][0] = s_code

                res[-1][2][0][1].append(t_code)
            else:
                if res[-1][2][-1][0] != s_code:
                    res[-1][2].append(['', []])
                    res[-1][2][-1][0] = s_code
                    res[-1][2][-1][1].append(t_code)
                else:
                    res[-1][2][-1][1].append(t_code)
    del res[0]
    return res


# главная функция
def get_info_from_excel(filename):

    xls = xlrd.open_workbook(filename)
    xls = xls.sheet_by_index(0)

    # преобразуем обьект Sheet в матрицу python
    matrix = [
        [xls.cell_value(i, j) for j in range(xls.ncols)]
        for i in range(xls.nrows)
    ]
    
    # удаляем пустые строки
    for i in range(len(matrix))[::-1]:
        if len(list(filter(bool, matrix[i])))==0: del matrix[i]

    # размеры матрицы
    rows, cols = len(matrix), len(matrix[0])

    # создаем массив диапазонов "Обязательной", "Формируемой" (части), "Факультативов", "ГИА"
    parts = []
    k = 0
    for i in range(cols):
        if matrix[1][i] != '':
            parts += [range(k, i)]
            k = i
    del parts[0]

    skill_types = []
    k = 0
    for i in range(rows)[1::]:
        if matrix[i][2] == '' and matrix[i+1][2] != '':
            skill_types += [range(k, i)]
            k = i
    del skill_types[0]
    skill_types += [range(k, rows)]
    
    data = {}

    # парсим title
    mas = matrix[0][0].split('"')
    program_name = mas[1]
    mas = matrix[0][0].split()
    for el in mas: 
        if el.count('.') == 2:
            program_code = el
        if el.count('/') == 1:
            temp = el.split('/')
            year_start = temp[0]
            year_end = temp[1]
    
    # заполняем data всеми дисциплинами и их данными
    for c in range(cols)[3::]:
        key = matrix[2][c]
        data[key] = {}
        data[key]['program_name'] = program_name
        data[key]['program_code'] = program_code
        data[key]['year_start'] = year_start
        data[key]['year_end'] = year_end
        data[key]['part_type'] = get_part_type(matrix, c)

        # основной алгоритм заполнения данных для docx таблиц
        data[key]['universal_competentions'] = get_info_for_table(matrix, skill_types[0], c)
        data[key]['average_prof_competentions'] = get_info_for_table(matrix, skill_types[1], c)
        data[key]['prof_competentions'] = get_info_for_table(matrix, skill_types[2], c)

    return data
