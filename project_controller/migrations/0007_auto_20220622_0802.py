# Generated by Django 3.1.2 on 2022-06-22 08:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_controller', '0006_remove_app_is_auth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='project_path',
            field=models.TextField(default='/User/adefemioseni/Desktop/djuix_test_projects', editable=False),
        ),
    ]
