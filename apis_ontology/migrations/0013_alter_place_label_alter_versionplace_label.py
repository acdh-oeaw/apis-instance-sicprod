# Generated by Django 5.0.7 on 2024-09-16 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0012_alter_place_options_rename_name_place_label_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='label',
            field=models.CharField(blank=True, default='', max_length=4096),
        ),
        migrations.AlterField(
            model_name='versionplace',
            name='label',
            field=models.CharField(blank=True, default='', max_length=4096),
        ),
    ]
