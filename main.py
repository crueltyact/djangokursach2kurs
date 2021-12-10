
from py.parser import get_info_from_excel
import os

filename = 'templates/' + os.listdir('templates')[0]

data = get_info_from_excel(filename)

file = open('log.txt', 'w', encoding='utf-8')
for key in data.keys():
    file.write(str(data[key])+'\n')
file.close()