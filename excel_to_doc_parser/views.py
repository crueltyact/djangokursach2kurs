import datetime
import os.path
import os.path
import shutil
from difflib import SequenceMatcher
from os.path import join
from pathlib import Path

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseForbidden, FileResponse
from django.shortcuts import render, redirect
from docxtpl import DocxTemplate
from lxml import etree

from excel_to_doc_parser.models import CustomUser, Role, Document, Theme, WorkProgram, ProgramNames, \
    TimePlan, Module, Section
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
        context = {"hello": "hello", "custom_user": CustomUser.objects.get(user=request.user)}
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
    else:
        return HttpResponseForbidden()
    return render(request, "main.html", context)


@login_required(login_url='/login/')
def documents(request):
    context = {"documents": Document.objects.filter(user_id=request.user.id),
               "custom_user": CustomUser.objects.get(user=request.user), "disciplines": ProgramNames.objects.all()}
    context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
    if request.method == "POST":
        if request.POST.get("generate"):
            theme = Theme.objects.get(document_id=Document.objects.get(pk=request.POST.get("document")))
            path = join(str(BASE_DIR), "excel_to_doc_parser/media/excel")
            folder = join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files/docx")
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
            data, _ = get_info_from_excel(
                path + "/matrices/" + "09_03_03_Прикладная_информатика,"
                                      "_Матрица_Корпоративные_информационные_системы_2020.xlsx")
            discipline = Document.objects.get(pk=request.POST.get('document')).program_name.program_name
            data["program_name"] = discipline
            data["program_code"] = Document.objects.get(pk=request.POST.get('document')).program_name.work_program.program_code
            data["program_code"] = Document.objects.get(
                pk=request.POST.get('document')).program_name.work_program.profile_name
            data["program_code"] = Document.objects.get(
                pk=request.POST.get('document')).program_name.work_program.year_start
            data["current_year"] = datetime.date.today().year
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
            doc = DocxTemplate(
                join(str(BASE_DIR), "excel_to_doc_parser/templates/template.docx"))
            doc.render(dict(data[discipline], **context_plane))
            for i in range(len(doc.tables)):
                table = doc.tables[i]._tbl
                for row in doc.tables[i].rows:
                    if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
                        table.remove(row._tr)
            doc.save(join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files/docx/{}.docx".format(discipline)))
            context['path'] = "excel_to_doc_parser/media/generated_files/docx/{}.docx".format(discipline)
            context['name'] = discipline + '.docx'
            return redirect("/download/?file={}&name=".format(context['path'], context["name"]))
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
    return render(request, "./docx_creation/document.html", context)


def xml_parser():
    pass


@login_required(login_url='/login/')
def themes(request):
    context = {}
    if request.user.is_authenticated:
        context["custom_user"] = CustomUser.objects.get(user=request.user)
        context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
        if request.method == "GET":
            context["document"] = request.GET.get("document")
        if request.method == "POST":
            context["document"] = request.POST.get("document")
    # theme = Theme.objects.get(document_id=Document.objects.get(pk=request.GET.get("document")))
    # if request.user.is_authenticated:
    #     context["custom_user"] = CustomUser.objects.get(user=request.user)
    #     context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
    #     context["theme"] = Theme.objects.get(pk=theme.id)
    #     context["modules"] = Module.objects.filter(theme_id=Theme.objects.get(pk=theme.id))
    #     context["homework_hours"] = TimePlan.objects.get(program_name=Document.objects.get(pk=request.GET.get("document")).program_name).homework_hours
    #     context["classwork_hours"] = TimePlan.objects.get(program_name=Document.objects.get(pk=request.GET.get("document")).program_name).classwork_hours - context["homework_hours"]
    #     if len(context["modules"]) > 0:
    #         context["last_module"] = context["modules"].order_by('-id')[0].module
    #         context["sections"] = Section.objects.filter(theme_id=context["theme"])
    #     else:
    #         context["last_module"] = 0
    #     if request.method == "POST":
    #         if request.POST.get("generate"):
    #             path = join(str(BASE_DIR), "excel_to_doc_parser/media/excel")
    #             folder = join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files")
    #             for filename in os.listdir(folder):
    #                 file_path = os.path.join(folder, filename)
    #                 if filename == ".gitkeep":
    #                     continue
    #                 try:
    #                     if os.path.isfile(file_path) or os.path.islink(file_path):
    #                         os.unlink(file_path)
    #                     elif os.path.isdir(file_path):
    #                         shutil.rmtree(file_path)
    #                 except Exception as e:
    #                     print('An error appear ' + str(e))
    #             data, _ = get_info_from_excel(
    #                 path + "/matrices/" + "09_03_03_Прикладная_информатика,"
    #                                       "_Матрица_Корпоративные_информационные_системы_2020.xlsx")
    #             discipline = Document.objects.get(pk=request.GET['document']).program_name.program_name
    #             data["program_name"] = discipline
    #             data["program_code"] = Document.objects.get(pk=request.GET['document']).program_name.work_program.program_code
    #             data["program_code"] = Document.objects.get(
    #                 pk=request.GET['document']).program_name.work_program.profile_name
    #             data["program_code"] = Document.objects.get(
    #                 pk=request.GET['document']).program_name.work_program.year_start
    #             data["current_year"] = datetime.date.today().year
    #             print(data[discipline])
    #             try:
    #                 context_plane = get_info_from_education_plane(path + "/planes/03-5190 - ВЕБ 2020 (1).xlsx")[
    #                     discipline]
    #             except KeyError:
    #                 for error_key in get_info_from_education_plane(path + "/planes/planes/03-5190 - ВЕБ 2020 ("
    #                                                                       "1).xlsx"):
    #                     if SequenceMatcher(None, discipline, error_key).ratio() >= 0.75:
    #                         context_plane = \
    #                             get_info_from_education_plane(path + "/planes/planes/03-5190 -"
    #                                                                  " ВЕБ 2020 (1).xlsx")[error_key]
    #                         break
    #             context_plane['intensity_ZET_check'] = check_number(context_plane['intensity_ZET'])
    #             context_plane['intensity_hours_check'] = check_number(context_plane['intensity_hours'])
    #             context_plane['total_homework_hours_check'] = check_number(context_plane['total_homework_hours'])
    #             for i, _ in enumerate(context_plane['courses']):
    #                 context_plane['courses'][i]['ZET_check'] = check_number(context_plane['courses'][i]['ZET'])
    #                 context_plane['courses'][i]['hours_check'] = check_number(context_plane['courses'][i]['hours'])
    #                 context_plane['courses'][i]['homework_time_check'] = check_number(
    #                     context_plane['courses'][i]['homework_time'])
    #             context_plane["modules"] = Module.objects.filter(theme_id=Theme.objects.get(pk=theme.id))
    #             if len(context["modules"]) > 0:
    #                 context_plane["sections"] = Section.objects.filter(theme_id=context["theme"])
    #             doc = DocxTemplate(
    #                 join(str(BASE_DIR), "excel_to_doc_parser/templates/template.docx"))
    #             doc.render(dict(data[discipline], **context_plane))
    #             for i in range(len(doc.tables)):
    #                 table = doc.tables[i]._tbl
    #                 for row in doc.tables[i].rows:
    #                     if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
    #                         table.remove(row._tr)
    #             doc.save(join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files/{}.docx".format(discipline)))
    #             context['path'] = "excel_to_doc_parser/media/generated_files/{}.docx".format(discipline)
    #             context['name'] = discipline + '.docx'
    #             return redirect("/download/?file={}&name=".format(context['path'], context["name"]))
    #         if request.POST.get("new_section"):
    #             header = request.POST.get('new_header')
    #             description = request.POST.get('new_description')
    #             classwork_hours = request.POST.get('new_classwork')
    #             homework_hours = request.POST.get('new_homework')
    #             semester = request.POST.get('new_semester')
    #             week = request.POST.get('new_week')
    #             module = request.POST.get('new_module')
    #             theme = request.POST.get("new_theme")
    #             new_module = Section(module_id=Module.objects.get(pk=module), theme_id=Theme.objects.get(pk=theme),
    #                                  header=header, description=description,
    #                                  classwork_hours=classwork_hours, homework_hours=homework_hours, semester=semester,
    #                                  week=week)
    #             new_module.save()
    #             return redirect("./docx_creation/themes/?document={}".format(request.GET.get("document")))
    #         elif request.POST.get("new_module"):
    #             print(request.POST.get("theme"))
    #             new_module = Module(module=int(request.POST.get("last_module")) + 1,
    #                                 theme_id_id=request.POST.get("theme"))
    #             new_module.save()
    #             return redirect("./docx_creation/themes/?document={}".format(request.GET.get("document")))
    #         else:
    #             pk = request.POST.get('pk')
    #             header = request.POST.get('header')
    #             description = request.POST.get('description')
    #             classwork_hours = request.POST.get('classwork')
    #             homework_hours = request.POST.get('homework')
    #             semester = request.POST.get('semester')
    #             week = request.POST.get('week')
    #             module = Section.objects.filter(pk=pk)
    #             module.update(header=header, description=description, classwork_hours=classwork_hours,
    #                           homework_hours=homework_hours, semester=semester, week=week)
    #             return redirect("./docx_creation/themes/?document={}".format(request.GET.get("document")))
    return render(request, "./docx_creation/theme.html", context)


@login_required(login_url='/login/')
def document_information(request):
    context = {}
    if request.user.is_authenticated:
        context["custom_user"] = CustomUser.objects.get(user=request.user)
        context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
        context["document"] = request.POST.get("document")
        context["theme"] = Document.objects.get(pk=request.POST.get("document")).program_name.program_name
        if request.method == "POST":
            pass
    return render(request, "./docx_creation/targets.html", context)


@login_required(login_url='/login/')
def generate_xml(request):
    root = etree.Element("root")
    tree = etree.ElementTree(root)
    desc = etree.Element("discipline")
    desc.text = Document.objects.get(pk=request.POST.get("document")).program_name.program_name
    root.append(desc)
    prof = etree.Element("profile")
    prof.text = Document.objects.get(pk=request.POST.get("document")).program_name.work_program.profile_name
    root.append(prof)
    course = etree.Element("course")
    course.text = "#TODO"
    root.append(course)
    status = etree.Element("status")
    status.text = Document.objects.get(pk=request.POST.get("document")).status.status
    root.append(status)
    elective = etree.Element("elective")
    elective.text = "#TODO"
    root.append(elective)
    files = etree.Element("files")
    files_list = ["rpd", "annotation", "fos", "method", "review", "plan", "matrix", "program"]
    try:
        for element in files_list:
            file = etree.Element(element)
            file.text = "#TODO"
            files.append(file)
    except Exception as exc:
        print(exc)
    root.append(files)
    targets = etree.Element("targets")
    try:
        for element in request.POST.get("targets").split(";") or "":
            target = etree.Element("target")
            target.text = element
            targets.append(target)
    except Exception as exc:
        print(exc)
    root.append(targets)
    tasks = etree.Element("tasks")
    try:
        for element in request.POST.get("tasks").split(";") or "":
            task = etree.Element("task")
            task.text = element
            tasks.append(task)
    except Exception as exc:
        print(exc)
    root.append(tasks)
    sections = etree.Element("sections")
    try:
        for element in request.POST.get("sections").split(";") or "":
            section_name = etree.Element("section_name")
            section_name.text = "#TODO"
            sections.append(section_name)
            hours = etree.Element("hours")
            hours.text = "#TODO"
            sections.append(hours)
    except Exception as exc:
        print(exc)
    root.append(sections)
    disciplines = etree.Element("disciplines")
    try:
        for element in request.POST.get("disciplines").split(";") or "":
            discipline = etree.Element("discipline")
            discipline.text = "#TODO"
            disciplines.append(discipline)
    except Exception as exc:
        print(exc)
    root.append(disciplines)
    sections_content = etree.Element("sections_content")
    try:
        for element in request.POST.get("sections_content").split(";") or "":
            theme = etree.Element("theme")
            theme.text = "#TODO"
            sections_content.append(theme)
            hours = etree.Element("hours")
            hours.text = "#TODO"
            sections_content.append(hours)
            content = etree.Element("content")
            content.text = "#TODO"
            sections_content.append(content)
    except Exception as exc:
        print(exc)
    root.append(sections_content)
    marks = etree.Element("marks")
    competency = etree.Element("competency")
    competency.text = "#TODO"
    marks.append(competency)
    attestation = etree.Element("attestation")
    attestation.text = "#TODO"
    marks.append(attestation)
    brs = etree.Element("brs")
    brs.text = "#TODO"
    marks.append(brs)
    brs_description = etree.Element("brs_description")
    brs_description.text = "#TODO"
    marks.append(brs_description)
    competencies = etree.Element("competencies")
    try:
        for element in request.POST.get("competencies").split(";") or "":
            competency = etree.Element("theme")
            competency.text = "#TODO"
            competencies.append(competency)
    except Exception as exc:
        print(exc)
    marks.append(competencies)
    intermediate = etree.Element("intermediate")
    try:
        for element in request.POST.get("intermediate").split(";") or "":
            mark = etree.Element("mark")
            value = etree.Element("value")
            competency.text = "#TODO"
            mark.append(value)
            characteristics = etree.Element("characteristics")
            characteristics.text = "#TODO"
            mark.append(characteristics)
            intermediate.append(mark)
    except Exception as exc:
        print(exc)
    marks.append(intermediate)
    root.append(marks)
    literature = etree.Element("literature")
    main = etree.Element("main")
    try:
        for element in request.POST.get("main").split(";") or "":
            book = etree.Element("book")
            book.text = "#TODO"
            main.append(book)
    except Exception as exc:
        print(exc)
    literature.append(main)
    additional = etree.Element("additional")
    try:
        for element in request.POST.get("additional").split(";") or "":
            book = etree.Element("book")
            book.text = "#TODO"
            additional.append(book)
    except Exception as exc:
        print(exc)
    literature.append(additional)
    digital = etree.Element("digital")
    try:
        for element in request.POST.get("digital").split(";") or "":
            resources = etree.Element("resources")
            resources.text = "#TODO"
            digital.append(resources)
    except Exception as exc:
        print(exc)
    literature.append(digital)
    root.append(literature)
    software = etree.Element("software")
    try:
        for element in request.POST.get("software").split(";") or "":
            program = etree.Element("program")
            program.text = "#TODO"
            software.append(program)
    except Exception as exc:
        print(exc)
    root.append(software)
    evaluation_tools = etree.Element("evaluation_tools")
    try:
        for element in request.POST.get("evaluation_tools").split(";") or "":
            tool = etree.Element("tool")
            tool.text = "#TODO"
            evaluation_tools.append(tool)
    except Exception as exc:
        print(exc)
    root.append(evaluation_tools)
    tasks = etree.Element("tasks")
    try:
        for element in request.POST.get("tasks").split(";") or "":
            task = etree.Element("task")
            task.text = "#TODO"
            tasks.append(task)
    except Exception as exc:
        print(exc)
    root.append(tasks)
    path_to_save = join(str(BASE_DIR), "excel_to_doc_parser\\media\\generated_files\\xml\\{}".format(request.user.id))
    Path(path_to_save).mkdir(parents=True, exist_ok=True)
    filename = "{}-{}.xml".format(Document.objects.get(pk=request.POST.get("document")).program_name.program_name,
                                  datetime.date.today().strftime("%m.%d.%Y"))
    tree.write(join(str(BASE_DIR), path_to_save, filename), encoding="UTF-8", xml_declaration=True, pretty_print=True)


@login_required(login_url='/login/')
def result(request):
    context = {}
    if request.user.is_authenticated:
        context["custom_user"] = CustomUser.objects.get(user=request.user)
        context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
        context["document"] = request.POST.get("document")
        if request.method == "POST":
            if request.POST.get("end") == "generate":
                generate_xml(request)
            if request.POST.get("save"):
                pass
                # path = join(str(BASE_DIR), "excel_to_doc_parser/media/excel")
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
                # data, _ = get_info_from_excel(
                #     path + "/matrices/" + "09_03_03_Прикладная_информатика,"
                #                           "_Матрица_Корпоративные_информационные_системы_2020.xlsx")
                # discipline = Document.objects.get(pk=request.POST.get('document')).program_name.program_name
                # data["program_name"] = discipline
                # data["program_code"] = Document.objects.get(pk=request.POST.get('document')).program_name.work_program.program_code
                # data["program_code"] = Document.objects.get(
                #     pk=request.GET['document']).program_name.work_program.profile_name
                # data["program_code"] = Document.objects.get(
                #     pk=request.GET['document']).program_name.work_program.year_start
                # data["current_year"] = datetime.date.today().year
                # print(data[discipline])
                # try:
                #     context_plane = get_info_from_education_plane(path + "/planes/03-5190 - ВЕБ 2020 (1).xlsx")[
                #         discipline]
                # except KeyError:
                #     for error_key in get_info_from_education_plane(path + "/planes/planes/03-5190 - ВЕБ 2020 ("
                #                                                           "1).xlsx"):
                #         if SequenceMatcher(None, discipline, error_key).ratio() >= 0.75:
                #             context_plane = \
                #                 get_info_from_education_plane(path + "/planes/planes/03-5190 -"
                #                                                      " ВЕБ 2020 (1).xlsx")[error_key]
                #             break
                # context_plane['intensity_ZET_check'] = check_number(context_plane['intensity_ZET'])
                # context_plane['intensity_hours_check'] = check_number(context_plane['intensity_hours'])
                # context_plane['total_homework_hours_check'] = check_number(context_plane['total_homework_hours'])
                # for i, _ in enumerate(context_plane['courses']):
                #     context_plane['courses'][i]['ZET_check'] = check_number(context_plane['courses'][i]['ZET'])
                #     context_plane['courses'][i]['hours_check'] = check_number(context_plane['courses'][i]['hours'])
                #     context_plane['courses'][i]['homework_time_check'] = check_number(
                #         context_plane['courses'][i]['homework_time'])
                # context_plane["modules"] = Module.objects.filter(theme_id=Theme.objects.get(pk=theme.id))
                # if len(context["modules"]) > 0:
                #     context_plane["sections"] = Section.objects.filter(theme_id=context["theme"])
                # doc = DocxTemplate(
                #     join(str(BASE_DIR), "excel_to_doc_parser/templates/template.docx"))
                # doc.render(dict(data[discipline], **context_plane))
                # for i in range(len(doc.tables)):
                #     table = doc.tables[i]._tbl
                #     for row in doc.tables[i].rows:
                #         if len(row.cells[0].text.strip()) == 0 and len(set(row.cells)) == 1:
                #             table.remove(row._tr)
                # doc.save(join(str(BASE_DIR), "excel_to_doc_parser/media/generated_files/{}.docx".format(discipline)))
                # context['path'] = "excel_to_doc_parser/media/generated_files/{}.docx".format(discipline)
                # context['name'] = discipline + '.docx'
                # return redirect("/download/?file={}&name=".format(context['path'], context["name"]))
    return render(request, "./docx_creation/result.html", context)


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


@login_required(login_url='/login/')
def info(request):
    context = {}
    if request.user.is_authenticated:
        context["custom_user"] = CustomUser.objects.get(user=request.user)
        context["role"] = Role.objects.get(pk=context["custom_user"].role_id)
    return render(request, "feedback.html", context)
