import os.path
import shutil
import urllib
from os import listdir
from os.path import isfile, join
from wsgiref.util import FileWrapper

from django.http import HttpResponse
from django.shortcuts import render
from docxtpl import DocxTemplate

from excel_to_doc_parser.py.parser import get_info_from_excel
from parser_server.settings import BASE_DIR


def index(request):
    context = {}
    path = join(str(BASE_DIR), "excel_to_doc_parser/media/excel")
    files_dict = {}
    folder = join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files")
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('An error appear ' + str(e))
    for file in listdir(path):
        if isfile(join(path, file)):
            files_dict[" ".join(file.split(',')[1][:-5].split("_")[2:])] = file
    if request.method == "GET":
        context['step'] = 1
        profiles = []
        for key in files_dict:
            profiles.append(key)
        context['profiles'] = profiles
    if request.method == "POST":
        context['step'] = 2
        data = get_info_from_excel(
            path + "/" + files_dict[request.POST.get("profile")])
        context['data'] = data
        context['profile'] = request.POST.get('profile')
        if request.POST.get('discipline'):
            context['step'] = 3
            discipline = request.POST.get('discipline')
            doc = DocxTemplate(
                join(str(BASE_DIR), "excel_to_doc_parser/templates/template.docx"))
            doc.render(data[discipline])
            for i in range(len(doc.tables)):
                table = doc.tables[i]._tbl
                for row in doc.tables[i].rows:
                    if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
                        table.remove(row._tr)
            doc.save(join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files/{}.docx".format(
                data[discipline]['program_name'])))
            context['path'] = "excel_to_doc_parser/media/generated_files/{}.docx".format(
                data[discipline]['program_name'])
            context['name'] = data[discipline]['program_name'] + '.docx'
    return render(request, "index.html", context)


def download(request):
    file = join(str(BASE_DIR), request.GET.get('file'))
    print(file)
    name = urllib.parse.quote(request.GET.get('name'), encoding='utf-8')
    filename = open(file, 'rb')
    content = FileWrapper(filename)
    response = HttpResponse(content, content_type='application/vnd.openxmlformats-officedocument.wordprocessingml'
                                                  '.document')
    response['Content-Length'] = os.path.getsize(file)
    response['Content-Disposition'] = 'attachment; filename*=utf-8\'\'{}'.format(
        name)
    print(response['Content-Disposition'])
    return response
