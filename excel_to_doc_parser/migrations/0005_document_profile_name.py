# Generated by Django 4.1.2 on 2023-03-01 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excel_to_doc_parser', '0004_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='profile_name',
            field=models.CharField(default='', max_length=512),
        ),
    ]