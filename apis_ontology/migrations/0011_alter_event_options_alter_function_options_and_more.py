# Generated by Django 5.0.7 on 2024-09-16 06:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0010_remove_versionfunction_collection_collection_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='function',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='institution',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['name', 'first_name']},
        ),
        migrations.AlterModelOptions(
            name='place',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='salary',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='versionevent',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical event', 'verbose_name_plural': 'historical events'},
        ),
        migrations.AlterModelOptions(
            name='versionfunction',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical function', 'verbose_name_plural': 'historical functions'},
        ),
        migrations.AlterModelOptions(
            name='versioninstitution',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical institution', 'verbose_name_plural': 'historical institutions'},
        ),
        migrations.AlterModelOptions(
            name='versionperson',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical person', 'verbose_name_plural': 'historical persons'},
        ),
        migrations.AlterModelOptions(
            name='versionplace',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical place', 'verbose_name_plural': 'historical places'},
        ),
        migrations.AlterModelOptions(
            name='versionsalary',
            options={'get_latest_by': ('history_date', 'history_id'), 'ordering': ('-history_date', '-history_id'), 'verbose_name': 'historical salary', 'verbose_name_plural': 'historical salarys'},
        ),
    ]