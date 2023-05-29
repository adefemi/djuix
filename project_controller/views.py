from rest_framework.viewsets import ModelViewSet
from abstractions.defaults import (
    DEFAULT_PROJECT_DIR, OPTIONAL_PACKAGES, PACKAGE_LIST, UserStatuses
)
from app_controller.models import ModelInfo
from app_controller.services.write_view import WriteToView
from controllers.directory_controller import DirectoryManager
from djuix.auth_middleware import IsAuthenticatedSpecial
from djuix.custom_methods import download_zip, setup_for_download, download_project
from djuix.utils import get_query
from project_controller.services.write_auth import WriteAuth
from project_controller.services.write_url import WriteProjectUrl
from .services.write_settings_file import WriteSettings
from rest_framework.views import APIView
import os
import time

from project_controller.services.write_utils import WriteUtils

from .services.process_app_creation import process_app_creation
from .serializers import (
    Project, ProjectSerializer, App, AppSerializer, ProjectSettings, ProjectAuth,
    ProjectSettingSerializer, RunMigrationSerializer, ProjectAuthSerializer
)
from controllers.terminal_controller import TerminalController
from rest_framework.response import Response
from djuix.helper import Helper
from djuix.functions import send_process_message
from user_management.models import UserStatus
from .models import TestServer

from project_templates.blog.process import CreateBlogTemplate
from .services.test_server_creation import TestServerCreation
from djuix.tasks import remove_test_server
from django.utils import timezone
from datetime import timedelta


class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = "slug"

    def deleteProjectStatus(self):
        UserStatus.objects.filter(
            user_id=self.request.user.id,
            operation=UserStatuses.create_project.value).delete()

    def get_queryset(self):
        data = self.request.query_params.dict()
        data.pop("page", None)
        keyword = data.pop("keyword", None)

        results = self.queryset.filter(
            owner_id=self.request.user.id).filter(**data)

        if keyword:
            search_fields = (
                "name", "formatted_name"
            )
            query = get_query(keyword, search_fields)
            results = results.filter(query)

        return results

    def create(self, request, *args, **kwargs):
        active_user = request.user

        if active_user.project_owner.all().count() == active_user.project_count:
            raise Exception(
                f"You have reached your limit of {active_user.project_count} project creations. To free up space, please delete one of your existing projects.")

        data = Helper.normalizer_request(request.data)
        template = data.pop("template", None)
        description = data.get("description", None)
        if not description:
            data["description"] = f"This is a default description for your {data.get('name','Django')} project."

        UserStatus.objects.create(
            user_id=active_user.id, operation=UserStatuses.create_project.value)

        default_project_path = DEFAULT_PROJECT_DIR

        delete_if_project_exist = data.get("delete_if_project_exist", False)
        if delete_if_project_exist:
            Project.objects.filter(
                name=data["name"], owner_id=active_user.id).delete()
        else:
            proj = Project.objects.filter(
                name=data["name"], owner_id=active_user.id)
            if proj:
                self.deleteProjectStatus()
                raise Exception(
                    f"A project with name '{data['name']}' already exists")

        data["owner_id"] = active_user.id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("delete_if_project_exist", None)
        serializer.save()

        send_process_message(active_user.id, "initializing project...")
        project_path = serializer.data["project_path"]
        active_project = self.queryset.get(id=serializer.data["id"])

        terminal_controller = TerminalController(
            default_project_path,
            active_project,
            delete_if_project_exist,
            active_user.id)

        try:
            terminal_controller.create_project()
            project_path = terminal_controller.path
            active_project.project_path = project_path
            active_project.save()
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            self.deleteProjectStatus()
            raise Exception(e)

        try:
            settings_c = WriteSettings(active_project)
            settings_c.update_package_on_setting(PACKAGE_LIST)
            settings_c.create_setting()
            print("settings created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            self.deleteProjectStatus()
            raise Exception(e)

        # create some basic project artifacts
        WriteUtils(active_project)

        if template == "blog":
            print("start creating blog template")
            send_process_message(active_user.id, "Creating blog template...")
            try:
                CreateBlogTemplate(active_project)
                send_process_message(
                    active_user.id, "Creating blog template migrations...")
                terminal_controller.run_migration()
                active_project.has_migration = True
                active_project.save()
                ModelInfo.objects.filter(app__project_id=active_project.id).update(
                    has_created_migration=True)
            except Exception as e:
                active_project.delete()
                self.deleteProjectStatus()
                raise Exception(e)

        send_process_message(active_user.id, "All done!")
        send_process_message(active_user.id, "", 0, True)
        UserStatus.objects.filter(
            user_id=active_user.id, operation=UserStatuses.create_project.value).delete()

        return Response(self.serializer_class(active_project).data, status=201)

    def destroy(self, request, *args, **kwargs):
        active_project = self.get_object()
        DirectoryManager.delete_directory(active_project.project_path)
        return super().destroy(request, *args, **kwargs)


class AppView(ModelViewSet):
    serializer_class = AppSerializer
    queryset = App.objects.select_related("project")

    def get_queryset(self):
        query = self.request.query_params
        queryset = self.queryset.filter(project__owner_id=self.request.user.id)

        if query.get("get_app_by_project_id", None) is not None:
            id = query["get_app_by_project_id"]
            queryset = queryset.filter(project__slug=id)

        return queryset

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)
        description = data.get("description", None)
        if not description:
            data["description"] = f"This is a default description for your {data.get('name','Django')} app."
        app = process_app_creation(data)

        WriteProjectUrl(app.project)
        app.project.save()  # update project

        return Response(self.get_serializer(app).data, status="201")


class RunMigrationView(ModelViewSet):
    http_method_names = ("post",)
    serializer_class = RunMigrationSerializer

    def create(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)

        active_project = Project.objects.get(
            id=data.validated_data["project_id"], owner_id=request.user.id)
        if not active_project:
            raise Exception("Project not found")

        terminal_controller = TerminalController(
            active_project.project_path, active_project)

        terminal_controller.run_migration()

        active_project.run_migration = False
        active_project.has_migration = True
        active_project.save()

        # update project models on migration status
        ModelInfo.objects.filter(app__project_id=active_project.id).update(
            has_created_migration=True)

        return Response("Migration created successfully")


class SettingsView(ModelViewSet):
    serializer_class = ProjectSettingSerializer
    queryset = ProjectSettings.objects.select_related("project")
    lookup_field = "project__slug"

    def get_queryset(self):
        return super().get_queryset().filter(project__owner_id=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        self.settings_obj = self.get_object().properties

        final_res = {}
        self.handle_get_environment(final_res)
        self.handle_get_database(final_res)
        self.handle_get_storage(final_res)
        self.handle_get_email(final_res)

        return Response(final_res)

    def handle_get_environment(self, obj):
        obj["environment"] = {
            "DEBUG": self.settings_obj["DEBUG"]["value"],
            "LANGUAGE_CODE": self.settings_obj["LANGUAGE_CODE"]["value"],
            "TIME_ZONE": self.settings_obj["TIME_ZONE"]["value"],
            "USE_TZ": True if self.settings_obj["USE_TZ"]["value"] == "True" else False,
        }

    def handle_get_database(self, obj):
        obj["database"] = {
            "engine": self.settings_obj["DATABASES"]["properties"]["key"],
        }

        if self.settings_obj["DATABASES"]["properties"]["key"] == "postgres":
            obj["database"]["DB_NAME"] = self.settings_obj["DATABASES"]["properties"]["NAME"]
            obj["database"]["DB_HOST"] = self.settings_obj["DATABASES"]["properties"]["HOST"]
            obj["database"]["DB_USER"] = self.settings_obj["DATABASES"]["properties"]["USER"]
            obj["database"]["DB_PORT"] = self.settings_obj["DATABASES"]["properties"]["PORT"]
            obj["database"]["DB_PASSWORD"] = self.settings_obj["DATABASES"]["properties"]["PASSWORD"]

    def handle_get_storage(self, obj):
        engine = None
        if self.settings_obj.get('AWS_ACCESS_KEY_ID', None):
            engine = "aws"
        elif self.settings_obj.get('CLOUDINARY_STORAGE', None):
            engine = "cloudinary"

        obj["storage"] = {
            "engine": engine,
        }

        if engine == "aws":
            obj["storage"]["AWS_ACCESS_KEY_ID"] = self.settings_obj["AWS_ACCESS_KEY_ID"]["value"]
            obj["storage"]["AWS_SECRET_ACCESS_KEY"] = self.settings_obj["AWS_SECRET_ACCESS_KEY"]["value"]
            obj["storage"]["AWS_STORAGE_BUCKET_NAME"] = self.settings_obj["AWS_STORAGE_BUCKET_NAME"]["value"]

        if engine == "cloudinary":
            obj["storage"]["CLOUD_NAME"] = self.settings_obj["CLOUDINARY_STORAGE"]["value"]["CLOUD_NAME"]
            obj["storage"]["API_KEY"] = self.settings_obj["CLOUDINARY_STORAGE"]["value"]["API_KEY"]
            obj["storage"]["API_SECRET"] = self.settings_obj["CLOUDINARY_STORAGE"]["value"]["API_SECRET"]

    def handle_get_email(self, obj):
        engine = None
        if self.settings_obj.get('EMAIL_BACKEND', None):
            engine = "email"

        obj["email"] = {
            "engine": engine,
        }

        if engine == "email":
            obj["email"]["HOST"] = self.settings_obj.get(
                'EMAIL_HOST', {}).get("value", None)
            obj["email"]["PORT"] = self.settings_obj.get(
                'EMAIL_PORT', {}).get("value", None)
            obj["email"]["USE_TLS"] = self.settings_obj.get(
                'USE_TLS', {}).get("value", None)
            obj["email"]["HOST_USER"] = self.settings_obj.get(
                'EMAIL_HOST_USER', {}).get("value", None)
            obj["email"]["PASSWORD"] = self.settings_obj.get(
                'EMAIL_HOST_PASSWORD', {}).get("value", None)
            obj["email"]["DEFAULT_FROM_EMAIL"] = self.settings_obj.get(
                'DEFAULT_FROM_EMAIL', {}).get("value", None)

    def control_env(self, state="delete"):
        env_path = os.path.join(
            self.terminal_controller.get_project_full_path(), ".env")
        if state == "delete":
            try:
                DirectoryManager.delete_file(env_path)
            except:
                pass  # ignore file does not exist

        else:
            dir_manager = DirectoryManager(env_path)
            env_file = dir_manager.create_file("")
            DirectoryManager.write_file(env_file, self.env_content)
            print("wrote env file to")

    def update(self, request, *args, **kwargs):
        # keys to deal with: Environment, database, filestorage, email
        request_body = Helper.normalizer_request(request.data)
        active_setting = self.get_object()
        self.c_packages = PACKAGE_LIST
        current_aws = str(active_setting.properties.get('AWS_ACCESS_KEY_ID', '')) + str(active_setting.properties.get(
            'AWS_SECRET_ACCESS_KEY', '')) + str(active_setting.properties.get('AWS_STORAGE_BUCKET_NAME', ''))
        current_cloudinary = str(
            active_setting.properties.get('CLOUDINARY_STORAGE', ''))

        current_db = str(active_setting.properties["DATABASES"])

        self.terminal_controller = TerminalController(
            active_setting.project.project_path, active_setting.project)

        # clear out .env file
        self.control_env()
        self.env_content = ""

        self.settings_obj = active_setting.properties

        env_data = request_body.get("environment", None)
        if env_data:
            self.handle_env_update(env_data)

        database_data = request_body.get("database", None)
        if database_data:
            self.handle_database_update(database_data)

        filestorage_data = request_body.get("storage", None)
        if filestorage_data:
            self.handle_filestorage_update(filestorage_data)

        email_data = request_body.get("email", None)
        if email_data:
            self.handle_email_update(email_data)

        active_setting.save()
        self.terminal_controller.install_packages(self.c_packages)
        self.terminal_controller.finalize_process()

        new_props = self.get_object().properties
        new_db = str(self.get_object().properties["DATABASES"])

        write_settings = WriteSettings(active_setting.project)
        write_settings.update_setting(new_props)

        if self.env_content:
            self.control_env("create")

        if new_db != current_db:
            active_setting.project.run_migration = True

        if {'AWS_ACCESS_KEY_ID', 'CLOUDINARY_STORAGE'} <= new_props.keys():
            if 'AWS_ACCESS_KEY_ID' in new_props.properties:
                new_aws = str(new_props.get('AWS_ACCESS_KEY_ID', '')) + str(new_props.get(
                    'AWS_SECRET_ACCESS_KEY', '')) + str(new_props.get('AWS_STORAGE_BUCKET_NAME', ''))
                if current_aws != new_aws:
                    active_setting.project.changed_storage = True
            elif 'CLOUDINARY_STORAGE' in new_props and current_cloudinary != str(new_props.get('CLOUDINARY_STORAGE', '')):
                active_setting.project.changed_storage = True

        active_setting.project.save()  # update the project

        return Response("settings updated")

    def handle_env_update(self, data):
        self.settings_obj["DEBUG"]["value"] = data.get(
            "DEBUG", self.settings_obj["DEBUG"]["value"])
        self.settings_obj["LANGUAGE_CODE"]["value"] = data.get(
            "LANGUAGE_CODE", self.settings_obj["LANGUAGE_CODE"]["value"])
        self.settings_obj["TIME_ZONE"]["value"] = data.get(
            "TIME_ZONE", self.settings_obj["TIME_ZONE"]["value"])
        self.settings_obj["USE_TZ"]["value"] = "True" if data["USE_TZ"] else "False"

    def handle_database_update(self, data):
        if data["engine"] == "postgres":
            self.settings_obj["DATABASES"]["properties"]["key"] = "postgres"
            self.settings_obj["DATABASES"]["properties"]["ENGINE"] = "django.db.backends.postgresql_psycopg2"
            self.settings_obj["DATABASES"]["properties"]["NAME"] = data["DB_NAME"]
            self.settings_obj["DATABASES"]["properties"]["HOST"] = data["DB_HOST"]
            self.settings_obj["DATABASES"]["properties"]["USER"] = data["DB_USER"]
            self.settings_obj["DATABASES"]["properties"]["PORT"] = data["DB_PORT"]
            self.settings_obj["DATABASES"]["properties"]["PASSWORD"] = data["DB_PASSWORD"]
            self.c_packages.append(OPTIONAL_PACKAGES['psycopg2'])

            self.env_content += f'DB_NAME={data["DB_NAME"]}\n'
            self.env_content += f'DB_HOST={data["DB_HOST"]}\n'
            self.env_content += f'DB_USER={data["DB_USER"]}\n'
            self.env_content += f'DB_PORT={data["DB_PORT"]}\n'
            self.env_content += f'DB_PASSWORD={data["DB_PASSWORD"]}\n'

        else:
            self.settings_obj["DATABASES"]["properties"]["key"] = "sqlite"
            self.settings_obj["DATABASES"]["properties"]["ENGINE"] = "django.db.backends.sqlite3"
            self.settings_obj["DATABASES"]["properties"][
                "NAME"] = 'os.path.join(BASE_DIR, "db.sqlite3")'
            self.settings_obj["DATABASES"]["properties"].pop('HOST', None)
            self.settings_obj["DATABASES"]["properties"].pop('PORT', None)
            self.settings_obj["DATABASES"]["properties"].pop('USER', None)
            self.settings_obj["DATABASES"]["properties"].pop('PASSWORD', None)

    def handle_filestorage_update(self, data):

        def clear_aws():
            self.settings_obj.pop('CLOUDINARY_STORAGE', None)
            try:
                self.settings_obj["INSTALLED_APPS"]["items"].remove(
                    "cloudinary_storage")
                self.settings_obj["INSTALLED_APPS"]["items"].remove(
                    "cloudinary")
            except Exception as e:
                print(e)
                pass

        def clear_cloudinary():
            self.settings_obj.pop('AWS_ACCESS_KEY_ID', None)
            self.settings_obj.pop('AWS_SECRET_ACCESS_KEY', None)
            self.settings_obj.pop('AWS_STORAGE_BUCKET_NAME', None)
            self.settings_obj.pop('AWS_S3_CUSTOM_DOMAIN', None)

        if data["engine"] == "aws":
            clear_aws()
            clear_cloudinary()
            self.settings_obj["AWS_ACCESS_KEY_ID"] = {
                "value": data["AWS_ACCESS_KEY_ID"],
                "is_string": True
            }
            self.settings_obj["AWS_SECRET_ACCESS_KEY"] = {
                "value": data["AWS_SECRET_ACCESS_KEY"],
                "is_string": True
            }
            self.settings_obj["AWS_STORAGE_BUCKET_NAME"] = {
                "value": data["AWS_STORAGE_BUCKET_NAME"],
                "is_string": True
            }
            self.settings_obj["AWS_S3_CUSTOM_DOMAIN"] = {
                "value": "f'{config(\"AWS_STORAGE_BUCKET_NAME\")}.s3.amazonaws.com'",
            }
            self.settings_obj["DEFAULT_FILE_STORAGE"] = {
                "value": "storages.backends.s3boto3.S3Boto3Storage",
                "is_string": True
            }

            self.env_content += f'\nAWS_ACCESS_KEY_ID={data["AWS_ACCESS_KEY_ID"]}\n'
            self.env_content += f'AWS_SECRET_ACCESS_KEY={data["AWS_SECRET_ACCESS_KEY"]}\n'
            self.env_content += f'AWS_STORAGE_BUCKET_NAME={data["AWS_STORAGE_BUCKET_NAME"]}\n'

            self.c_packages.append(OPTIONAL_PACKAGES["boto"])
            self.c_packages.append(OPTIONAL_PACKAGES["django_storages"])

        elif data["engine"] == "cloudinary":
            clear_cloudinary()
            clear_aws()
            self.settings_obj["CLOUDINARY_STORAGE"] = {
                "value": {
                    'CLOUD_NAME': data["CLOUD_NAME"],
                    'API_KEY':  data["API_KEY"],
                    'API_SECRET':  data["API_SECRET"]
                }
            }
            self.settings_obj["INSTALLED_APPS"]["items"].append(
                "cloudinary_storage")
            self.settings_obj["INSTALLED_APPS"]["items"].append("cloudinary")
            self.settings_obj["DEFAULT_FILE_STORAGE"] = {
                "value": "cloudinary_storage.storage.MediaCloudinaryStorage",
                "is_string": True
            }

            self.env_content += f'\nCLOUD_NAME={data["CLOUD_NAME"]}\n'
            self.env_content += f'API_KEY={data["API_KEY"]}\n'
            self.env_content += f'API_SECRET={data["API_SECRET"]}\n'

            self.c_packages.append(OPTIONAL_PACKAGES['cloudinary'])
            self.c_packages.append(OPTIONAL_PACKAGES['django_cloudinary'])

        else:
            clear_aws()
            clear_cloudinary()
            self.settings_obj.pop('DEFAULT_FILE_STORAGE', None)

    def handle_email_update(self, data):
        if data["engine"] == "email":
            self.settings_obj["EMAIL_BACKEND"] = {
                "value": 'django.core.mail.backends.smtp.EmailBackend',
                "is_string": True
            }
            self.settings_obj["EMAIL_HOST"] = {
                "value": data["HOST"],
                "is_string": True
            }
            self.settings_obj["EMAIL_PORT"] = {
                "value": data["PORT"],
            }
            self.settings_obj["USE_TLS"] = {
                "value": data["USE_TLS"],
            }
            self.settings_obj["EMAIL_HOST_USER"] = {
                "value": data["HOST_USER"],
                "is_string": True
            }
            self.settings_obj["EMAIL_HOST_PASSWORD"] = {
                "value": data["PASSWORD"],
                "is_string": True
            }
            self.settings_obj["DEFAULT_FROM_EMAIL"] = {
                "value": data["DEFAULT_FROM_EMAIL"],
                "is_string": True
            }

        else:
            self.settings_obj.pop('EMAIL_BACKEND', None)
            self.settings_obj.pop('EMAIL_HOST', None)
            self.settings_obj.pop('EMAIL_PORT', None)
            self.settings_obj.pop('USE_TLS', None)
            self.settings_obj.pop('EMAIL_HOST_USER', None)
            self.settings_obj.pop('EMAIL_HOST_PASSWORD', None)
            self.settings_obj.pop('DEFAULT_FROM_EMAIL', None)


class GetProjectUrls(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    http_method_names = ("get",)
    lookup_field = "slug"

    def get_queryset(self):
        return super().get_queryset().filter(owner_id=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        active_project = self.get_object()

        project_apps = active_project.project_apps.all()

        urls_array_dict = {
            "Admin Paths": [
                {
                    "path": "admin/",
                    "name": "Admin",
                    "description": "Manage your project with Django Admin Interface",
                }
            ]
        }

        for app in project_apps:
            app_urls = app.app_urls.all()
            base_path = f'{app.formatted_name}-path/'
            app_path_name = f"{app.name} Paths"
            urls_array_dict[app_path_name] = []
            for url in app_urls:
                temp_obj = {
                    "path": base_path + url.name,
                    "name": url.name.capitalize(),
                    "description": url.description
                }
                urls_array_dict[app_path_name].append(temp_obj)

        return Response(urls_array_dict)


class SetProjectAuth(ModelViewSet):
    serializer_class = ProjectAuthSerializer
    queryset = ProjectAuth.objects.all()

    def deleteAuthStatus(self):
        UserStatus.objects.filter(
            user_id=self.request.user.id, operation=UserStatuses.create_auth.value).delete()

    def get_queryset(self):
        return super().get_queryset().filter(project__owner_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        active_user = request.user
        validated_data = self.serializer_class(data=request.data)
        validated_data.is_valid(raise_exception=True)

        ProjectAuth.objects.filter(project__owner_id=active_user.id).delete()

        self.deleteAuthStatus()

        UserStatus.objects.create(
            user_id=active_user.id, operation=UserStatuses.create_auth.value)

        validated_data.save()

        active_project = Project.objects.get(
            id=validated_data.validated_data['project_id'])

        write_auth = WriteAuth(active_project)
        try:
            write_auth.setup_auth()
        except Exception as e:
            ProjectAuth.objects.filter(project_id=active_project.id).delete()
            self.deleteAuthStatus()
            raise Exception(e)

        UserStatus.objects.filter(
            user_id=active_user.id, operation=UserStatuses.create_auth.value).delete()
        active_project.run_migration = True
        active_project.save()
        return Response("Auth created successfully", status=201)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)

        active_obj = self.get_object()

        write_auth = WriteAuth(active_obj.project)
        try:
            write_auth.create_auth_model()
            write_auth.create_auth_utitlties()
            write_auth.finalize_process()
        except Exception as e:
            raise Exception(e)

        active_obj.project.run_migration = True
        active_obj.project.save()

        return Response("Auth updated successfully", status=201)

    def destroy(self, request, *args, **kwargs):
        active_project = self.get_object().project

        super().destroy(request, *args, **kwargs)

        active_project = Project.objects.get(id=active_project.id)

        # get all apps and remove permissions for them
        for i in active_project.project_apps.all():
            for j in i.app_views.all():
                props = j.field_properties
                if props.get("permission", None):
                    del props["permission"]
                j.field_properties = props
                j.save()

            WriteToView(i)

        write_auth = WriteAuth(active_project, True)
        write_auth.delete_auth()
        active_project.run_migration = True
        active_project.save()

        return Response("Auth deleted successfully")


class LoadProject(ModelViewSet):
    http_method_names = ("get",)
    permission_classes = [IsAuthenticatedSpecial]

    def get_queryset(self):
        return None

    def list(self, request, *args, **kwargs):
        active_user = request.user
        username = active_user.username.lower()
        if active_user.removed_folder:
            try:
                download_zip(DEFAULT_PROJECT_DIR, username, username)
            except:
                pass
            active_user.removed_folder = False
            active_user.save()
        return Response("Loaded successfully")


class DownloadProject(APIView):

    def get(self, request, id):
        try:
            active_project = Project.objects.get(id=id)
        except Exception:
            raise Exception("project not found")

        if not active_project.has_migration:
            raise Exception("project not ready for download")

        setup_for_download(active_project)

        download_link = download_project(active_project)

        return Response({"link": download_link})
    

class StartTestServerView(APIView):
    
    def get(self, request, id):
        active_project = self._get_project(id)
        self._check_project_migration(active_project)
        
        project_test_server = TestServer.objects.filter(project_id=active_project.id)
        if project_test_server.exists():
            self._destroy_existing_test_server(project_test_server.first())
        
        default_port = 5000
        port = self._get_next_available_port(default_port)

        test_server = TestServer.objects.create(
            project_id=active_project.id, 
            port=port,
            expiry=timezone.now() + timedelta(seconds=active_project.owner.test_server_timeout)
        )
        
        test_server_creation = TestServerCreation(test_server.project, test_server.port)
        
        try:
            result = test_server_creation.deploy()
            test_server.ip = result
            test_server.save()
        except Exception as e:
            test_server_creation.destroy()
            test_server.delete()
            raise Exception(e)
                
        remove_test_server.apply_async(args=[test_server.id], countdown=test_server.project.owner.test_server_timeout) 
        time.sleep(10)
        return Response({"message": result})

    def _get_project(self, id):
        try:
            return Project.objects.get(id=id)
        except Project.DoesNotExist:
            raise Exception("Project not found")

    def _check_project_migration(self, project):
        if not project.has_migration:
            raise Exception("Project has no migrations yet and not ready for testing")

    def _get_next_available_port(self, default_port):
        try:
            latest_test_server = TestServer.objects.latest('created_at')
            return latest_test_server.port + 1
        except TestServer.DoesNotExist:
            return default_port

    def _destroy_existing_test_server(self, test_server):
        test_server_creation = TestServerCreation(test_server.project, test_server.port)
        test_server_creation.destroy()
        test_server.delete()
        

class CloseTestServerView(APIView):
    
    def get(self, request, id):
        test_server = self._get_test_server(id)
        test_server_creation = TestServerCreation(test_server.project, test_server.port)
        
        try:
            test_server_creation.destroy()
            test_server.delete()
        except Exception as e:
            raise Exception(e)
        
        return Response({"message": "Test server closed"})
    def _get_test_server(self, id):
        try:
            project = Project.objects.get(id=id)
        except Project.DoesNotExist:
            raise Exception("Project not found")
        
        try:
            return project.project_test_server
        except Project.DoesNotExist:
            raise Exception("Project has no test server")
    
        
        