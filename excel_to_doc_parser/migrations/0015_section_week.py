# Generated by Django 4.0 on 2022-04-20 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('excel_to_doc_parser', '0014_section_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='week',
            field=models.IntegerField(default=1),
        ),
    ]
