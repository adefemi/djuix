# Generated by Django 3.1.2 on 2022-12-21 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project_controller', '0009_projectauth_default_auth'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectauth',
            name='default_auth',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
