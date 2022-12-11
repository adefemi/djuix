# Generated by Django 3.1.2 on 2022-12-09 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_controller', '0003_auto_20221113_0841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='formatted_name',
            field=models.CharField(editable=False, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='project_path',
            field=models.TextField(default='/Users/adefemioseni/Desktop/djuix_test_projects'),
        ),
        migrations.CreateModel(
            name='ProjectAuth',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('properties', models.JSONField(blank=True, null=True)),
                ('username_field', models.CharField(choices=[('email', 'email'), ('username', 'username')], default='email', max_length=10)),
                ('project', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='project_auth', to='project_controller.project')),
            ],
        ),
    ]
