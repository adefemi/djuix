# Generated by Django 3.1.2 on 2022-07-19 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_controller', '0015_project_run_migration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='run_migration',
            field=models.BooleanField(default=True),
        ),
    ]