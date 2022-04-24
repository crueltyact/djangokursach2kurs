import csv
import os.path
import shutil
import time
import urllib
from difflib import SequenceMatcher
from os import listdir
from os.path import isfile, join
from wsgiref.util import FileWrapper

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import FileSystemStorage
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.shortcuts import render, redirect
from docxtpl import DocxTemplate

from excel_to_doc_parser.models import CustomUser, Role, Document, Theme, Section, Module, WorkProgram, ProgramNames, \
    TimePlan
from excel_to_doc_parser.py.parser import get_info_from_excel
from excel_to_doc_parser.py.parser_plane import get_info_from_education_plane
from parser_server.settings import BASE_DIR, MEDIA_ROOT


def check_number(num):
    if num % 10 == 1 and num != 11:
        return '1'
    elif 1 < num % 10 < 5 and (num > 19 or num < 5):
        return '2'
    else:
        return '3'


@login_required(login_url='/login/')
def index(request):
    context = {}
    if request.user.is_authenticated:
        context["hello"] = "hello"
        context["custom_user"] = CustomUser.objects.get(user=request.user)
        context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
        if context["custom_user"].role_id == 1:
            if request.method == "POST":
                fs = FileSystemStorage()
                program = fs.save(request.FILES['work_program'].name, request.FILES['work_program'])
                time = fs.save(request.FILES['time_plane'].name, request.FILES['time_plane'])
                work_program, key_list = get_info_from_excel(join(MEDIA_ROOT, program))
                new_program, created = WorkProgram.objects.update_or_create(profile_name=work_program['profile_name'],
                                                                            program_code=work_program["program_code"],
                                                                            year_start=work_program["year_start"],
                                                                            year_end=work_program["year_end"])
                for key in key_list:
                    try:
                        time_plane = get_info_from_education_plane(join(MEDIA_ROOT, time))[key]
                    except KeyError:
                        for error_key in get_info_from_education_plane(join(MEDIA_ROOT, time)):
                            if SequenceMatcher(None, key, error_key).ratio() >= 0.75:
                                time_plane = get_info_from_education_plane(join(MEDIA_ROOT, time))[
                                    error_key]
                                break
                    new_program_name, created = ProgramNames.objects.update_or_create(work_program=new_program,
                                                                                      program_name=key)
                    new_time_plan, created = TimePlan.objects.update_or_create(program_name=new_program_name,
                                                                               classwork_hours=time_plane[
                                                                                   "intensity_hours"],
                                                                               homework_hours=time_plane[
                                                                                   "total_homework_hours"],
                                                                               intensity_ZET=time_plane[
                                                                                   "intensity_ZET"])
                folder = MEDIA_ROOT
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if filename == ".gitkeep":
                        continue
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('An error appear ' + str(e))
    #     context["custom_user"] = CustomUser.objects.get(user=request.user)
    #     context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
    #     context["theme"] = Theme.objects.get(theme=1)
    #     context["modules"] = Module.objects.filter(theme_id=Theme.objects.get(theme=1))
    #     if len(context["modules"]) > 0:
    #         context["last_module"] = context["modules"].order_by('-id')[0].module
    #         context["sections"] = Section.objects.filter(theme_id=context["theme"])
    #
    #     else:
    #         context["last_module"] = 0
    #     if request.method == "POST":
    #         if request.POST.get("new_section"):
    #             header = request.POST.get('new_header')
    #             description = request.POST.get('new_description')
    #             classwork_hours = request.POST.get('new_classwork')
    #             homework_hours = request.POST.get('new_homework')
    #             module = request.POST.get('new_module')
    #             theme = request.POST.get("new_theme")
    #             new_module = Section(module_id=Module.objects.get(pk=module), theme_id=Theme.objects.get(pk=theme),
    #                                  header=header, description=description,
    #                                  classwork_hours=classwork_hours, homework_hours=homework_hours)
    #             new_module.save()
    #             return redirect("/")
    #         elif request.POST.get("new_module"):
    #             print(request.POST.get("theme"))
    #             new_module = Module(module=int(request.POST.get("last_module")) + 1,
    #                                 theme_id_id=request.POST.get("theme"))
    #             new_module.save()
    #             return redirect("/")
    #         else:
    #             pk = request.POST.get('pk')
    #             header = request.POST.get('header')
    #             description = request.POST.get('description')
    #             classwork_hours = request.POST.get('classwork')
    #             homework_hours = request.POST.get('homework')
    #             module = Section.objects.filter(pk=pk)
    #             module.update(header=header, description=description, classwork_hours=classwork_hours,
    #                           homework_hours=homework_hours)
    #             with open(join(str(BASE_DIR), 'excel_to_doc_parser/media/temporary_text/{}.csv'.format(
    #                     str(request.user) + '_' + header)), 'w') as f:
    #                 writer = csv.writer(f)
    #                 writer.writerow(['header', 'description', 'classwork_hours', 'homework_hours'])
    #                 writer.writerow([header, description, classwork_hours, homework_hours])
    #             return redirect("/")
    # path = join(str(BASE_DIR), "excel_to_doc_parser/media/excel")
    # files_dict = {}
    # folder = join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files")
    # for filename in os.listdir(folder):
    #     file_path = os.path.join(folder, filename)
    #     if filename == ".gitkeep":
    #         continue
    #     try:
    #         if os.path.isfile(file_path) or os.path.islink(file_path):
    #             os.unlink(file_path)
    #         elif os.path.isdir(file_path):
    #             shutil.rmtree(file_path)
    #     except Exception as e:
    #         print('An error appear ' + str(e))
    # for file in listdir(join(path, "matrices")):
    #     if isfile(join(path, "matrices", file)):
    #         files_dict[" ".join(file.split(',')[1][:-5].split("_")[2:])] = file
    # if request.method == "GET":
    #     context['step'] = 1
    #     profiles = []
    #     for key in files_dict:
    #         profiles.append(key)
    #     context['profiles'] = profiles
    # if request.method == "POST":
    #     context['step'] = 2
    #     data = get_info_from_excel(
    #         path + "/matrices/" + files_dict[request.POST.get("profile")])
    #     context['data'] = data
    #     context['profile'] = request.POST.get('profile')
    #     if request.POST.get('discipline'):
    #         context['step'] = 3
    #         discipline = request.POST.get('discipline')
    #         try:
    #             context_plane = get_info_from_education_plane(path + "/planes/03-5190 - ВЕБ 2020 (1).xlsx")[
    #                 discipline]
    #         except KeyError:
    #             for error_key in get_info_from_education_plane(path + "/planes/planes/03-5190 - ВЕБ 2020 (1).xlsx"):
    #                 if SequenceMatcher(None, discipline, error_key).ratio() >= 0.75:
    #                     context_plane = \
    #                         get_info_from_education_plane(path + "/planes/planes/03-5190 - ВЕБ 2020 (1).xlsx")[
    #                             error_key]
    #                     break
    #         context_plane['intensity_ZET_check'] = check_number(context_plane['intensity_ZET'])
    #         context_plane['intensity_hours_check'] = check_number(context_plane['intensity_hours'])
    #         context_plane['total_homework_hours_check'] = check_number(context_plane['total_homework_hours'])
    #         for i, _ in enumerate(context_plane['courses']):
    #             context_plane['courses'][i]['ZET_check'] = check_number(context_plane['courses'][i]['ZET'])
    #             context_plane['courses'][i]['hours_check'] = check_number(context_plane['courses'][i]['hours'])
    #             context_plane['courses'][i]['homework_time_check'] = check_number(
    #                 context_plane['courses'][i]['homework_time'])
    #         doc = DocxTemplate(
    #             join(str(BASE_DIR), "excel_to_doc_parser/templates/template.docx"))
    #         doc.render(dict(data[discipline], **context_plane))
    #         for i in range(len(doc.tables)):
    #             table = doc.tables[i]._tbl
    #             for row in doc.tables[i].rows:
    #                 if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
    #                     table.remove(row._tr)
    #         doc.save(join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files/{}.docx".format(
    #             data[discipline]['program_name'])))
    #         context['path'] = "excel_to_doc_parser/media/generated_files/{}.docx".format(
    #             data[discipline]['program_name'])
    #         context['name'] = data[discipline]['program_name'] + '.docx'
    else:
        return HttpResponseForbidden()
    return render(request, "main.html", context)


@login_required(login_url='/login/')
def documents(request):
    context = {"documents": Document.objects.filter(user_id=request.user.id),
               "custom_user": CustomUser.objects.get(user=request.user), "disciplines": ProgramNames.objects.all()}
    if request.method == "POST":
        program_name = request.POST.get("program_name")
        link = request.POST.get("link")
        status = request.POST.get("status")
        user = request.user.id
        new_document = Document(link_id=link, status_id=status, user_id=user,
                                program_name=ProgramNames.objects.get(pk=ProgramNames.objects.get(program_name=program_name).id))
        new_document.save()
        new_theme = Theme(document_id=new_document)
        new_theme.save()
        return redirect('/documents')
    return render(request, "document.html", context)


@login_required(login_url='/login/')
def themes(request):
    context = {}
    theme = Theme.objects.get(document_id=Document.objects.get(pk=request.GET.get("document")))
    if request.user.is_authenticated:
        context["custom_user"] = CustomUser.objects.get(user=request.user)
        context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
        context["theme"] = Theme.objects.get(pk=theme.id)
        context["modules"] = Module.objects.filter(theme_id=Theme.objects.get(pk=theme.id))
        if len(context["modules"]) > 0:
            context["last_module"] = context["modules"].order_by('-id')[0].module
            context["sections"] = Section.objects.filter(theme_id=context["theme"])
        else:
            context["last_module"] = 0
        if request.method == "POST":
            if request.POST.get("generate"):
                path = join(str(BASE_DIR), "excel_to_doc_parser/media/excel")
                folder = join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files")
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if filename == ".gitkeep":
                        continue
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print('An error appear ' + str(e))
                data = get_info_from_excel(
                    path + "/matrices/" + "09_03_03_Прикладная_информатика,"
                                          "_Матрица_Корпоративные_информационные_системы_2020.xlsx")
                discipline = "Навыки эффективной презентации"
                try:
                    context_plane = get_info_from_education_plane(path + "/planes/03-5190 - ВЕБ 2020 (1).xlsx")[
                        discipline]
                except KeyError:
                    for error_key in get_info_from_education_plane(path + "/planes/planes/03-5190 - ВЕБ 2020 ("
                                                                          "1).xlsx"):
                        if SequenceMatcher(None, discipline, error_key).ratio() >= 0.75:
                            context_plane = \
                                get_info_from_education_plane(path + "/planes/planes/03-5190 -"
                                                                     " ВЕБ 2020 (1).xlsx")[error_key]
                            break
                context_plane['intensity_ZET_check'] = check_number(context_plane['intensity_ZET'])
                context_plane['intensity_hours_check'] = check_number(context_plane['intensity_hours'])
                context_plane['total_homework_hours_check'] = check_number(context_plane['total_homework_hours'])
                for i, _ in enumerate(context_plane['courses']):
                    context_plane['courses'][i]['ZET_check'] = check_number(context_plane['courses'][i]['ZET'])
                    context_plane['courses'][i]['hours_check'] = check_number(context_plane['courses'][i]['hours'])
                    context_plane['courses'][i]['homework_time_check'] = check_number(
                        context_plane['courses'][i]['homework_time'])
                context_plane["modules"] = Module.objects.filter(theme_id=Theme.objects.get(pk=theme.id))
                if len(context["modules"]) > 0:
                    context_plane["sections"] = Section.objects.filter(theme_id=context["theme"])
                doc = DocxTemplate(
                    join(str(BASE_DIR), "excel_to_doc_parser/templates/template.docx"))
                doc.render(dict(data[discipline], **context_plane))
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
                return redirect("/download/?file={}&name=".format(context['path'], context["name"]))
            if request.POST.get("new_section"):
                header = request.POST.get('new_header')
                description = request.POST.get('new_description')
                classwork_hours = request.POST.get('new_classwork')
                homework_hours = request.POST.get('new_homework')
                semester = request.POST.get('new_semester')
                week = request.POST.get('new_week')
                module = request.POST.get('new_module')
                theme = request.POST.get("new_theme")
                new_module = Section(module_id=Module.objects.get(pk=module), theme_id=Theme.objects.get(pk=theme),
                                     header=header, description=description,
                                     classwork_hours=classwork_hours, homework_hours=homework_hours, semester=semester,
                                     week=week)
                new_module.save()
                return redirect("/themes/?document={}".format(request.GET.get("document")))
            elif request.POST.get("new_module"):
                print(request.POST.get("theme"))
                new_module = Module(module=int(request.POST.get("last_module")) + 1,
                                    theme_id_id=request.POST.get("theme"))
                new_module.save()
                return redirect("/themes/?document={}".format(request.GET.get("document")))
            else:
                pk = request.POST.get('pk')
                header = request.POST.get('header')
                description = request.POST.get('description')
                classwork_hours = request.POST.get('classwork')
                homework_hours = request.POST.get('homework')
                semester = request.POST.get('semester')
                week = request.POST.get('week')
                module = Section.objects.filter(pk=pk)
                module.update(header=header, description=description, classwork_hours=classwork_hours,
                              homework_hours=homework_hours, semester=semester, week=week)
                # with open(join(str(BASE_DIR), 'excel_to_doc_parser/media/temporary_text/{}.csv'.format(
                #         str(request.user) + '_' + header)), 'w') as f:
                #     writer = csv.writer(f)
                #     writer.writerow(['header', 'description', 'classwork_hours', 'homework_hours'])
                #     writer.writerow([header, description, classwork_hours, homework_hours])
                return redirect("/themes/?document={}".format(request.GET.get("document")))
    return render(request, "theme.html", context)


def download(request):
    file = join(str(BASE_DIR), request.GET.get('file'))
    response = FileResponse(open(file, 'rb'), as_attachment=True,
                            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Length'] = os.path.getsize(file)
    return response


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        username = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            print("Error")
    return render(request, "authorization.html")


def logout_view(request):
    logout(request)
    if not request.user.is_authenticated:
        return redirect("/")
    return render(request, "authorization.html")
