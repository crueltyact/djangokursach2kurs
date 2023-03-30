from django.contrib.auth.models import User
from django.db import models


class Role(models.Model):
    ADMIN = 1
    DEAN = 2
    HOD = 3
    HEP = 4
    TEACHER = 5
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (DEAN, 'Dean'),
        (HOD, 'HOD'),
        (HEP, 'HEP'),
        (TEACHER, 'Teacher')
    )
    role_type = models.CharField(choices=ROLE_CHOICES, max_length=128)


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    second_name = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)


class Link(models.Model):
    link = models.CharField(max_length=256)


class Status(models.Model):
    STATUSES = [("В архиве", "archive"), ("Актуальный", "actual"), ("Отправлен на доработку", "revise"),
                ("Отклонён", "rejected"), ("В процессе составления", "making"),
                ("В процессе редакции", "redaction"), ("Составлен", "made"), ("Согласован", "conformed"),
                ("Утверждён", "approved")]
    status = models.CharField(choices=STATUSES, default=STATUSES[4], max_length=256)


class Document(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    link_to_xml = models.ForeignKey(Link, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=512, default="")
    profile_name = models.CharField(max_length=512, default="")
    program_code = models.CharField(max_length=512, default="")
