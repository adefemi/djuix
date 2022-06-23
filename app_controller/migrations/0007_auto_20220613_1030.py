# Generated by Django 3.1.2 on 2022-06-13 10:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project_controller', '0006_remove_app_is_auth'),
        ('app_controller', '0006_auto_20201123_0405'),
    ]

    operations = [
        migrations.CreateModel(
            name='UrlInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_properties', models.JSONField(default=None, null=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('app', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_urls', to='project_controller.app')),
            ],
        ),
        migrations.CreateModel(
            name='ViewsInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_properties', models.JSONField(default=None, null=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('app', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_views', to='project_controller.app')),
            ],
        ),
        migrations.RemoveField(
            model_name='serializerfield',
            name='serializer_main',
        ),
        migrations.AddField(
            model_name='modelinfo',
            name='field_properties',
            field=models.JSONField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='serializerinfo',
            name='field_properties',
            field=models.JSONField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='serializerinfo',
            name='app',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='app_serializers', to='project_controller.app'),
        ),
        migrations.AlterUniqueTogether(
            name='modelinfo',
            unique_together={('app_id', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='serializerinfo',
            unique_together={('app_id', 'name')},
        ),
        migrations.DeleteModel(
            name='ModelField',
        ),
        migrations.DeleteModel(
            name='SerializerField',
        ),
        migrations.AddField(
            model_name='viewsinfo',
            name='model',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='model_views', to='app_controller.modelinfo'),
        ),
        migrations.AddField(
            model_name='viewsinfo',
            name='serializer_relation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='serializer_views', to='app_controller.serializerinfo'),
        ),
        migrations.AddField(
            model_name='urlinfo',
            name='view_relation',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='view_urls', to='app_controller.viewsinfo'),
        ),
        migrations.AlterUniqueTogether(
            name='viewsinfo',
            unique_together={('app_id', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='urlinfo',
            unique_together={('app_id', 'name')},
        ),
    ]