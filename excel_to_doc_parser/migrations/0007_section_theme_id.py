# Generated by Django 4.0 on 2022-04-12 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('excel_to_doc_parser', '0006_remove_document_theme_remove_module_section_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='theme_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='excel_to_doc_parser.theme'),
            preserve_default=False,
        ),
    ]
