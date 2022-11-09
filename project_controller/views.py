from rest_framework.viewsets import ModelViewSet
from abstractions.defaults import OPTIONAL_PACKAGES, PACKAGE_LIST
from app_controller.models import ModelInfo
from controllers.directory_controller import DirectoryManager
from project_controller.models import ProjectSettings
from project_controller.services.write_url import WriteProjectUrl
from .services.write_settings_file import WriteSettings

from project_controller.services.write_utils import WriteUtils

from .services.process_app_creation import process_app_creation
from .serializers import Project, ProjectSerializer, App, AppSerializer, ProjectSettingSerializer, RunMigrationSerializer
from controllers.terminal_controller import TerminalController
from rest_framework.response import Response
from djuix.helper import Helper

from project_templates.blog.process import CreateBlogTemplate


class ProjectView(ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()
    lookup_field = "slug"

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)
        template = data.pop("template", None)
        
        delete_if_project_exist = data.get("delete_if_project_exist", False)
        if delete_if_project_exist:
            Project.objects.filter(name=data["name"]).delete() 
        else:
            proj = Project.objects.filter(name=data["name"])
            if proj:
                raise Exception(f"A project with name '{data['name']}' already exists")   
                
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("delete_if_project_exist", None)
        serializer.save()
        
        project_path = serializer.data["project_path"]
        active_project = self.queryset.get(id=serializer.data["id"])

        terminal_controller = TerminalController(project_path, active_project.formatted_name, delete_if_project_exist)

        try:
            terminal_controller.create_project()
            project_path = terminal_controller.path
            active_project.project_path = project_path
            active_project.save()
            print("project created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)

        try:
            settings_c = WriteSettings(active_project)
            settings_c.update_package_on_setting(PACKAGE_LIST)
            settings_c.create_setting()
            print("settings created")
        except Exception as e:
            self.queryset.filter(id=serializer.data["id"]).delete()
            print(e)
            raise Exception(e)
        
        # create some basic project artifacts
        WriteUtils(active_project)
        
        if template == "blog":
            print("start creating blog template")
            try:
                CreateBlogTemplate(active_project)
                terminal_controller.run_migration()
                ModelInfo.objects.filter(app__project_id=active_project.id).update(has_created_migration=True)
            except Exception as e:
                active_project.delete()
                raise Exception(e)

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
        queryset = self.queryset
        
        if query.get("get_app_by_project_id", None) is not None:
            id = query["get_app_by_project_id"]
            queryset = queryset.filter(project__slug = id)
            
        return queryset

    def create(self, request, *args, **kwargs):
        app = process_app_creation(request.data)
        
        WriteProjectUrl(app.project)
        app.project.save() # update project

        return Response(self.get_serializer(app).data, status="201")
    

class RunMigrationView(ModelViewSet):
    http_method_names = ("post",)
    serializer_class = RunMigrationSerializer
    
    def create(self, request, *args, **kwargs):
        data = self.get_serializer(data=request.data)
        data.is_valid(raise_exception=True)
        
        active_project = Project.objects.get(id=data.validated_data["project_id"])
        
        terminal_controller = TerminalController(active_project.project_path, active_project.formatted_name)
        
        terminal_controller.run_migration()
        
        active_project.run_migration = False
        active_project.save()
        
        # update project models on migration status
        ModelInfo.objects.filter(app__project_id=active_project.id).update(has_created_migration=True)
        
        return Response("Migration created successfully")
    

class SettingsView(ModelViewSet):
    serializer_class = ProjectSettingSerializer
    queryset = ProjectSettings.objects.select_related("project")
    lookup_field = "project__slug"
    
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
            "USE_TZ": True if self.settings_obj["USE_TZ"]["value"] == "True" else False
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
            obj["email"]["HOST"] = self.settings_obj.get('EMAIL_HOST', {}).get("value", None)
            obj["email"]["PORT"] = self.settings_obj.get('EMAIL_PORT', {}).get("value", None)
            obj["email"]["USE_TLS"] = self.settings_obj.get('USE_TLS', {}).get("value", None)
            obj["email"]["HOST_USER"] = self.settings_obj.get('EMAIL_HOST_USER', {}).get("value", None)
            obj["email"]["PASSWORD"] = self.settings_obj.get('EMAIL_HOST_PASSWORD', {}).get("value", None)
            obj["email"]["DEFAULT_FROM_EMAIL"] = self.settings_obj.get('DEFAULT_FROM_EMAIL', {}).get("value", None)
        
    
    def update(self, request, *args, **kwargs):
        # keys to deal with: Environment, database, filestorage, email
        request_body = Helper.normalizer_request(request.data)
        active_setting = self.get_object()
        self.settings_obj = active_setting.properties
        self.c_packages = PACKAGE_LIST
        
        env_data = request_body.get("environment", None)
        if env_data:
            self.handle_env_update(env_data)
            
        databse_data = request_body.get("database", None)
        if databse_data:
            self.handle_database_update(databse_data)
            
        filestorage_data = request_body.get("storage", None)
        if filestorage_data:
            self.handle_filestorage_update(filestorage_data)
        
        email_data = request_body.get("email", None)
        if email_data:
            self.handle_email_update(email_data)
            
        active_setting.properties = self.settings_obj
        active_setting.save()
        
        terminal_controller = TerminalController(active_setting.project.project_path, active_setting.project.formatted_name)
        terminal_controller.install_packages(self.c_packages)
        
        write_settings = WriteSettings(active_setting.project)
        write_settings.update_setting(self.get_object().properties)
        
        active_setting.project.save() # update the project
        
        return Response("settings updated")
    
    def handle_env_update(self, data):
        self.settings_obj["DEBUG"]["value"] = data.get("DEBUG", self.settings_obj["DEBUG"]["value"])
        self.settings_obj["LANGUAGE_CODE"]["value"] = data.get("LANGUAGE_CODE", self.settings_obj["LANGUAGE_CODE"]["value"])
        self.settings_obj["TIME_ZONE"]["value"] = data.get("TIME_ZONE", self.settings_obj["TIME_ZONE"]["value"])
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
            
        else:
            self.settings_obj["DATABASES"]["properties"]["key"] = "sqlite"
            self.settings_obj["DATABASES"]["properties"]["ENGINE"] = "django.db.backends.sqlite3"
            self.settings_obj["DATABASES"]["properties"]["NAME"] = 'os.path.join(BASE_DIR, "db.sqlite3")'
            self.settings_obj["DATABASES"]["properties"].pop('HOST', None)
            self.settings_obj["DATABASES"]["properties"].pop('PORT', None)
            self.settings_obj["DATABASES"]["properties"].pop('USER', None)
            self.settings_obj["DATABASES"]["properties"].pop('PASSWORD', None)
            
        self.get_object().project.run_migration = True
        self.get_object().project.save()
    
    def handle_filestorage_update(self, data):
        
        def clear_aws():
            self.settings_obj.pop('CLOUDINARY_STORAGE', None)
            try:
                self.settings_obj["INSTALLED_APPS"]["items"].remove("cloudinary_storage")
                self.settings_obj["INSTALLED_APPS"]["items"].remove("cloudinary")
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
                "value": "'{}.s3.amazonaws.com'".format(data["AWS_STORAGE_BUCKET_NAME"]),
            }
            self.settings_obj["DEFAULT_FILE_STORAGE"] = {
                "value": "storages.backends.s3boto3.S3Boto3Storage",
                "is_string": True
            }
            
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
            self.settings_obj["INSTALLED_APPS"]["items"].append("cloudinary_storage")
            self.settings_obj["INSTALLED_APPS"]["items"].append("cloudinary")
            self.settings_obj["DEFAULT_FILE_STORAGE"] = {
                "value": "cloudinary_storage.storage.MediaCloudinaryStorage",
                "is_string": True
            }
            
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
    
    def retrieve(self, request, *args, **kwargs):
        active_project = self.get_object()
        project_apps = active_project.project_apps.all()
        
        urls_array_dict = {
            "Admin Paths": [
                {
                    "path": "admin/",
                    "name": "Admin"
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
                    "name": url.name.capitalize()
                }
                urls_array_dict[app_path_name].append(temp_obj)
                
        return Response(urls_array_dict)
        
