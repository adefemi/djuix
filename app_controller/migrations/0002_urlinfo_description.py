# Generated by Django 3.1.4 on 2023-01-02 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_controller', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='urlinfo',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]