# Generated by Django 3.1.2 on 2022-03-29 15:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('project_controller', '0005_auto_20211231_0651'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='app',
            name='is_auth',
        ),
    ]