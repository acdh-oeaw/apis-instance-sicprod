# Generated by Django 4.2.10 on 2024-03-14 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0005_alter_event_metadata_alter_function_metadata_and_more'),
        ('apis_metainfo', '0011_alter_rootobject_deprecated_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='function',
            name='name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='institution',
            name='name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='person',
            name='name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='place',
            name='name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Name'),
        ),
        migrations.AddField(
            model_name='salary',
            name='name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Name'),
        ),
    ]