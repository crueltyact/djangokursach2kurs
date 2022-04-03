from django.contrib.auth.models import User
from django.db import models


class Role(models.Model):
    role_type = models.CharField(max_length=128)


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    second_name = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)


class Link(models.Model):
    link = models.CharField(max_length=256)


class Status(models.Model):
    STATUSES = [("В архиве", "archive"), ("Актуальный", "actual"), ("Отправлен на доработку", "revise"), ("Отклонён", "rejected"), ("В процессе составления", "making"),
    ("В процессе редакции", "redaction"), ("Составлен", "made"), ("Согласован", "conformed"), ("Утверждён", "approved")]
    status = models.CharField(choices=STATUSES, default=STATUSES[4], max_length=256)


class Document(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    module = models.IntegerField()
    header = models.CharField(max_length=128)
    semester = models.IntegerField()
    classwork_hours = models.IntegerField()
    homework_hours = models.IntegerField()
    description = models.TextField()



