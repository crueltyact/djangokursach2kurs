import xlrd


def get_matrix(filename):
    xls = xlrd.open_workbook(filename)
    xls = xls.sheet_by_index(0)
    return [
        [str(xls.cell_value(i, j)).strip() for j in range(xls.ncols)]
        for i in range(xls.nrows)
    ]


def find_cell(cell, matrix, full=True):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if full:
                if matrix[i][j] == cell:
                    return [i, j]
            else:
                if matrix[i][j] in cell:
                    return [i, j]
    return False


def left_cell(pos, matrix):
    r, c = pos
    c -= 1
    while matrix[r][c] == '':
        c -= 1
    return [r, c]


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


def get_courses(arr, rc):
    courses = list(map(lambda el: [el[0] + 1, el[1]], enumerate(arr[rc[1][1]:rc[1][1] + 8:])))
    courses = list(filter(lambda el: el[1] != '', courses))
    courses = list(map(lambda el: [el[0], float(el[1])], courses))
    courses_count = len(courses)
    res = []
    for sem, time in courses:
        res += [{}]
        res[-1]['semester'] = number_to_words(sem)
        res[-1]['course'] = number_to_words(int(round(sem / 2 + 0.1)))
        res[-1]['test'] = 'экзамен' if str(sem) in arr[rc[3][1]] else 'зачет'
        try:
            res[-1]['ZET'] = int(float(arr[rc[0][1]])) // courses_count
            res[-1]['hours'] = res[-1]['ZET'] * 36
            res[-1]['homework_time'] = int(res[-1]['hours'] - time)
        except Exception as e:
            print(e)
            return 0
    return res


def to_int(x):
    try:
        return int(float(x))
    except Exception as e:
        print(e)
        return x


# главная функция
def get_info_from_education_plane(filename):
    # получаем матрицу из файла
    matrix = get_matrix(filename)
    # ищем нужные координаты ячеек от которых будем отталкиваться
    end_r = find_cell('Факультативные дисциплины', matrix)[0]
    rc = {
        0: find_cell('Всего, ЗЕТ', matrix),
        1: find_cell('Распределение по курсам и семестрам, ауд. час.', matrix),
        2: find_cell('Обязательная часть', matrix),
        3: find_cell('экзаменов', matrix),
        4: find_cell('зачетов', matrix),
        5: find_cell('Самостоятельная работа', matrix),
    }
    # номер столбца с клетками как "Б.1"
    dc = left_cell([rc[2][0], rc[2][1]], matrix)[1]
    # преобразуем названия дисциплин к нормальному виду
    for i in range(len(matrix))[rc[2][0]::]:
        matrix[i][rc[2][1]] = matrix[i][rc[2][1]].split('*')[0].strip()
    # создаем и заполняем выходную структуру
    data = {}
    for i in range(len(matrix))[rc[2][0]:end_r + 1:]:
        if (len(list(filter(bool, matrix[i][rc[2][1] + 1::]))) != 0 and
                matrix[i][dc] == '' and
                matrix[i][rc[0][1]] != ''):
            key = matrix[i][rc[2][1]]
            data[key] = {}
            data[key]['intensity_ZET'] = to_int(matrix[i][rc[0][1]])
            data[key]['intensity_hours'] = data[key]['intensity_ZET'] * 36
            total_homework_hours = to_int(matrix[i][rc[5][1]])
            if type(total_homework_hours) == int:
                data[key]['total_homework_hours'] = total_homework_hours
            courses = get_courses(matrix[i], rc)
            if len(courses) > 0:
                data[key]['semesters'] = courses
    return data
