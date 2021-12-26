import xlrd


def get_matrix(filename):
    xls = xlrd.open_workbook(filename)
    xls = xls.sheet_by_index(0)

    return [
        [str(xls.cell_value(i, j)).strip() for j in range(xls.ncols)]
        for i in range(xls.nrows)
    ]


def number_to_words(n):
    less_than_ten = {1: 'первом', 2: 'втором', 3: 'третьем', 4: 'четвёртом',
                     5: 'пятом', 6: 'шестом', 7: 'седьмом', 8: 'восьмом',
                     9: 'девятом'}
    ten = {10: 'десятом'}
    from_eleven_to_nineteen = {11: 'одиннадцатом', 12: 'двенадцатом',
                               13: 'тринадцатом', 14: 'четырнадцатом',
                               15: 'пятнадцатом', 16: 'шестнадцатом',
                               17: 'семнадцатом', 18: 'восемнадцатом',
                               19: 'девятнадцатом'}
    n1 = n % 10
    n2 = n - n1
    if n < 10:
        return less_than_ten.get(n)
    elif 10 < n < 20:
        return from_eleven_to_nineteen.get(n)
    elif n >= 10 and n in ten:
        return ten.get(n)
    else:
        return ten.get(n2) + ' ' + less_than_ten.get(n1)


def hours_to_zet(z):
    h = round(z / 36, 1)
    if h == int(h):

        return int(h)
    else:
        return h


def get_courses(arr, imp_cols, met='moduls'):
    if met == 'practice':
        sems = [
                   to_int(el) for el in arr[imp_cols['exam']].replace(' ', '').split(',')
               ] + [
                   to_int(el) for el in arr[imp_cols['credit']].replace(' ', '').split(',')
               ]
        sems = list(filter(lambda x: x != 0, sems))
        return [{
            'semester': number_to_words(sem),
            'course': number_to_words(int(round(sem / 2 + 0.1))),
            'test': 'экзамен' if str(sem) in arr[imp_cols['exam']] else 'зачет',
            'hours': to_int(arr[imp_cols['ZET']]) * 36,
            'ZET': to_int(arr[imp_cols['ZET']]),
            'homework_time': 0,
        } for sem in sems]

    if met == 'elective':
        sem = to_int(arr[imp_cols['elective_sem']])
        hours = to_int(arr[imp_cols['elective_hours']])
        return [{
            'semester': number_to_words(sem),
            'course': number_to_words(int(round(sem / 2 + 0.1))),
            'test': 'зачет',
            'hours': hours,
            'ZET': hours_to_zet(hours),
            'homework_time': 0,
        }]

    # преобразуем courses к виду [[курс, часы аудиторной работы]]
    courses = list(map(lambda el: [el[0] + 1, el[1]], enumerate(arr[imp_cols['sems']::])))
    courses = list(filter(lambda el: el[1] != '', courses))
    courses = list(map(lambda el: [el[0], float(el[1])], courses))

    courses_count = len(courses)
    all_homework = to_int(arr[imp_cols['homework']])

    # алгоритм расчета часов домашней работы
    homeworks = [[sem, time / 2] for sem, time in courses]
    if sum([el[1] for el in homeworks]) != all_homework:
        homeworks = [[sem, time] for sem, time in courses]
    if sum([el[1] for el in homeworks]) != all_homework:
        div = all_homework // courses_count
        ost = all_homework % courses_count
        homeworks = [[sem, div] for sem, _ in courses]
        idx = [el[1] for el in courses].index(max([el[1] for el in courses]))
        homeworks[idx][1] += ost
    homeworks = dict(homeworks)

    # создаем и заполняем массив информации о каждом семестре
    res = []
    for sem, time in courses:
        res += [{}]
        res[-1]['semester'] = number_to_words(sem)
        res[-1]['course'] = number_to_words(int(round(sem / 2 + 0.1)))
        res[-1]['test'] = 'экзамен' if str(sem) in arr[imp_cols['exam']] else 'зачет'

        res[-1]['hours'] = to_int(time)
        res[-1]['ZET'] = hours_to_zet(res[-1]['hours'])

        res[-1]['homework_time'] = to_int(homeworks[sem])

    return res


def to_int(x):
    try:
        return int(float(x))
    except:
        return 0


def find_from_matrix(dct, matrix, idx=0):
    rev = dict([[val, key] for key, val in dct.items()])
    res = {}
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] in dct.values() and not rev[matrix[i][j]] in res.keys():
                res[rev[matrix[i][j]]] = i if idx == 0 else j
    return res


# главная функция
def get_info_from_education_plane(filename):
    # получаем матрицу из файла
    matrix = get_matrix(filename)

    # ищем нужные координаты ячеек от которых будем отталкиваться
    imp_rows = find_from_matrix({
        'subjects': 'Обязательная часть',
        'practice': 'Б.2',
        'elective': 'Факультативные дисциплины',
    }, matrix, 0)

    imp_cols = find_from_matrix({
        'credit': 'зачетов',
        'exam': 'экзаменов',
        'hours': 'ВСЕГО по структуре',
        'ZET': 'Всего, ЗЕТ',
        'homework': 'Самостоятельная работа',
        'sems': 'Распределение по курсам и семестрам, ауд. час.',
        'subjects': 'Обязательная часть',
        'B.1': 'Б.1',
        'elective': 'Факультативные дисциплины',
        'elective_sem': 'Семестр',
        'elective_hours': 'Ауд. часов',
    }, matrix, 1)

    # преобразуем названия дисциплин к нормальному виду
    for i in range(len(matrix))[imp_rows['subjects']::]:
        matrix[i][imp_cols['subjects']] = matrix[i][imp_cols['subjects']].split('*')[0].strip()

    # создаем и заполняем выходную структуру дисциплинами из блока "Модули"
    data = {}
    for i in range(imp_rows['subjects'], imp_rows['practice']):
        if matrix[i][imp_cols['hours']] != '' and matrix[i][imp_cols['B.1']] == '':
            key = matrix[i][imp_cols['subjects']]

            data[key] = {}

            data[key]['intensity_hours'] = to_int(matrix[i][imp_cols['hours']])
            data[key]['intensity_ZET'] = hours_to_zet(to_int(data[key]['intensity_hours']))
            data[key]['total_homework_hours'] = to_int(matrix[i][imp_cols['homework']])
            data[key]['courses'] = get_courses(matrix[i], imp_cols, met='moduls')

    # заполняем выходную структуру дисциплинами из блока "Практика" + "ГИА"
    for i in range(imp_rows['practice'], imp_rows['elective']):
        if matrix[i][imp_cols['B.1']] == '':
            key = matrix[i][imp_cols['subjects']]

            data[key] = {}

            data[key]['intensity_ZET'] = to_int(matrix[i][imp_cols['ZET']])
            data[key]['intensity_hours'] = data[key]['intensity_ZET'] * 36
            data[key]['total_homework_hours'] = 0
            data[key]['courses'] = get_courses(matrix[i], imp_cols, met='practice')

    # заполняем выходную структуру дисциплинами из блока "Факультативные дисциплины"
    i = imp_rows['elective'] + 1
    while matrix[i][imp_cols['elective']] != '':
        key = matrix[i][imp_cols['elective']]

        data[key] = {}
        data[key]['intensity_hours'] = to_int(matrix[i][imp_cols['elective_hours']])
        data[key]['intensity_ZET'] = hours_to_zet(data[key]['intensity_hours'])
        data[key]['total_homework_hours'] = 0
        data[key]['courses'] = get_courses(matrix[i], imp_cols, met='elective')

        i += 1

    return data
