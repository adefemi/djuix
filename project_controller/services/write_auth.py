

from abstractions.defaults import auth_app_name
from app_controller.services.write_model import WriteToModel
from controllers.directory_controller import DirectoryManager
from controllers.terminal_controller import TerminalController
from djuix.functions import send_process_message, write_to_file
from project_controller.services.write_settings_file import WriteSettings
from project_controller.services.write_url import WriteProjectUrl


class WriteAuth(TerminalController):
    auth_app_name = auth_app_name

    def __init__(self, project, isDel=False):
        self.project = project
        super().__init__(project.project_path, project, False, project.owner.id)
        if not isDel:
            self.project_auth = project.project_auth
            self.username_field = self.project.project_auth.username_field
        self.app_path = f"{self.path}/{self.project_name}/{self.auth_app_name}/"

        self.isDel = isDel

    def setup_auth(self):
        self.clean_up()
        send_process_message(self.project.owner.id,
                             f"creating {self.auth_app_name} app...")
        self.create_app(self.auth_app_name)
        self.install_packages()

        send_process_message(self.project.owner.id,
                             "Creating necessary models...")
        self.create_auth_model()

        send_process_message(self.project.owner.id,
                             "creating auth utilities...")
        self.create_auth_utitlties()
        self.create_auth_permission()

        send_process_message(self.project.owner.id,
                             "creating auth serializers...")
        self.create_serializer()

        send_process_message(self.project.owner.id, "creating auth views...")
        self.create_views()

        send_process_message(self.project.owner.id, "creating auth urls...")
        self.create_urls()

        send_process_message(self.project.owner.id, "finalizing process...", 0)
        self.finalize_process()
        send_process_message(self.project.owner.id, "All Done!")
        send_process_message(self.project.owner.id, "", 0, True)

    def delete_auth(self):
        self.clean_up()

        self.finalize_process()

    def delete_exist_db(self):
        # handle for sqlite database
        path = self.project.project_path + "/" + self.project.formatted_name.lower() + \
            "/db.sqlite3"
        try:
            DirectoryManager.delete_file(path)
        except:
            pass

    def create_auth_model(self):
        self.custom_username = f"{self.project.formatted_name.title()}CustomUser"
        # define imports
        data_content = "from django.db import models\n"
        data_content += "from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager\n"
        data_content += "from django.utils import timezone\n\n\n"

        data_content += f"class {self.custom_username}Manager(BaseUserManager):\n\n"
        data_content += f"\tdef create_user(self, {self.username_field}, password, **extra_fields):\n"
        data_content += f"\t\tif not {self.username_field}:\n"
        data_content += f"\t\t\traise ValueError('{self.username_field.title} field is required')\n\n"

        data_content += f"\t\tuser = self.model({self.username_field}={self.username_field}, **extra_fields)\n"
        data_content += f"\t\tuser.set_password(password)\n"
        data_content += f"\t\tuser.save()\n"
        data_content += f"\t\treturn user\n\n"

        data_content += f"\tdef create_superuser(self, {self.username_field}, password, **extra_fields):\n"
        data_content += f"\t\textra_fields.setdefault('is_staff', True)\n"
        data_content += f"\t\textra_fields.setdefault('is_superuser', True)\n"
        data_content += f"\t\textra_fields.setdefault('is_active', True)\n\n"

        data_content += f"\t\tif extra_fields.get('is_staff') is not True:\n"
        data_content += f"\t\t\traise ValueError('Superuser must have is_staff=True')\n\n"

        data_content += f"\t\tif extra_fields.get('is_superuser') is not True:\n"
        data_content += f"\t\t\traise ValueError('Superuser must have is_superuser=True')\n\n"

        data_content += f"\t\tself.create_user({self.username_field}, password, **extra_fields)\n\n\n"

        data_content += f"class {self.custom_username} (AbstractBaseUser, PermissionsMixin):\n\n"
        is_username = self.username_field == "username"
        data_content += f"\tusername = models.CharField(unique={is_username}, max_length=100, null={not is_username}, blank={not is_username})\n"
        data_content += f"\temail = models.EmailField(unique={not is_username}, null={is_username}, blank={is_username})\n"
        data_content += f"\tis_staff = models.BooleanField(default=False)\n"
        data_content += f"\tis_superuser = models.BooleanField(default=False)\n"
        data_content += f"\tis_active = models.BooleanField(default=True)\n"

        fields = self.project_auth.properties["fields"]

        has_slug, slug_data, data = WriteToModel.handle_model_fields(
            fields, data_content, self.get_formatted_name)
        data_content = data

        data_content = WriteToModel.format_has_created_date(data_content)
        data_content = WriteToModel.format_has_updated_date(data_content)

        data_content += f"\n\tUSERNAME_FIELD = '{self.username_field}'\n"
        data_content += f"\tobjects = {self.custom_username}Manager()\n\n"

        data_content = WriteToModel.format_string_representation(
            data_content, [self.username_field]) + "\n"
        data_content = WriteToModel.format_meta(
            data_content, {'ordering': "('created_at', )"}) + "\n"

        if has_slug:
            data_content = WriteToModel.format_slug(
                False, data_content, slug_data)
            data_content = WriteToModel.finalize_save(data_content)

        data_content += f"\nclass Jwt(models.Model):\n"
        data_content += f"\tuser = models.OneToOneField({self.custom_username}, related_name='login_user', on_delete=models.CASCADE)\n"
        data_content += f"\taccess = models.TextField()\n"
        data_content += f"\trefresh = models.TextField()\n"
        data_content = WriteToModel.format_has_created_date(data_content)
        data_content = WriteToModel.format_has_updated_date(data_content)

        write_to_file(self.app_path, "models.py", data_content)
        self.write_admin()

    def write_admin(self):
        # define imports
        data_content = "from django.contrib import admin\n"
        data_content += f"from .models import {self.custom_username}, Jwt\n\n"

        data_content += f"admin.site.register(({self.custom_username}, Jwt))\n"

        write_to_file(self.app_path, "admin.py", data_content)

    def create_auth_utitlties(self):
        # define imports
        data_content = "import jwt\n"
        data_content += "import random\n"
        data_content += "from django.conf import settings\n"
        data_content += "from datetime import datetime, timedelta\n"
        data_content += f"from .models import {self.custom_username}\n"
        data_content += "import string\n\n\n"

        data_content += f"def get_random(length):\n"
        data_content += f"\treturn ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))\n\n"

        data_content += f"def get_access_token(payload):\n"
        data_content += "\treturn jwt.encode({'exp': datetime.now() + timedelta(" + \
            f"minutes={self.project_auth.access_expiry}), **payload" + \
            "}, settings.SECRET_KEY, algorithm='HS256')\n\n"

        data_content += f"def get_refresh_token():\n"
        data_content += "\treturn jwt.encode({'exp': datetime.now() + timedelta(" + \
            f"days={self.project_auth.refresh_expiry}), 'data': get_random(10)" + \
            "}, settings.SECRET_KEY, algorithm='HS256')\n\n"

        data_content += f"def verify_token(token):\n"
        data_content += f"\ttry:\n"
        data_content += f"\t\tdecoded_data = jwt.decode(token, settings.SECRET_KEY, algorithm='HS256')\n"
        data_content += f"\texcept Exception:\n"
        data_content += f"\t\treturn None\n\n"
        data_content += f"\texp = decoded_data['exp']\n"
        data_content += f"\tif datetime.now().timestamp() > exp:\n"
        data_content += f"\t\treturn None\n\n"
        data_content += f"\treturn decoded_data\n\n"

        data_content += f"def decodeJWT(bearer):\n"
        data_content += f"\tif not bearer:\n"
        data_content += f"\t\treturn None\n\n"
        data_content += f"\ttoken = bearer[7:]\n"
        data_content += f"\tdecoded = verify_token(token)\n"
        data_content += f"\tif decoded:\n"
        data_content += f"\t\ttry:\n"
        data_content += f"\t\t\treturn {self.custom_username}.objects.get(id=decoded['user_id'])\n"
        data_content += f"\t\texcept Exception:\n"
        data_content += f"\t\t\treturn None\n"

        write_to_file(self.app_path, "utils.py", data_content)

    def create_auth_permission(self):
        # define imports
        data_content = "from rest_framework.permissions import BasePermission, SAFE_METHODS\n\n\n"

        data_content += f"class IsAuthenticatedCustom(BasePermission):\n\n"

        data_content += f"\tdef has_permission(self, request, view):\n"
        data_content += f"\t\tfrom .utils import decodeJWT\n"
        data_content += f"\t\tuser = decodeJWT(request.META.get('HTTP_AUTHORIZATION', None))\n"
        data_content += f"\t\tif not user:\n"
        data_content += f"\t\t\treturn False\n\n"
        data_content += f"\t\trequest.user = user\n"
        data_content += f"\t\tif request.user and request.user.is_authenticated:\n"
        data_content += f"\t\t\treturn True\n\n"
        data_content += f"\t\treturn False\n\n\n"

        data_content += f"class IsAuthenticatedOrReadOnlyCustom(BasePermission):\n\n"

        data_content += f"\tdef has_permission(self, request, view):\n"
        data_content += f"\t\tif request.method in SAFE_METHODS:\n"
        data_content += f"\t\t\treturn True\n\n"
        data_content += f"\t\tif request.user and request.user.is_authenticated:\n"
        data_content += f"\t\t\treturn True\n\n"
        data_content += f"\t\treturn False\n\n\n"

        write_to_file(self.app_path, "methods.py", data_content)

    def create_serializer(self):
        # define imports
        data_content = "from rest_framework import serializers\n"
        data_content += f"from .models import {self.custom_username}\n\n\n"

        is_email = self.username_field == "email"

        data_content += f"class LoginSerializer(serializers.Serializer):\n"
        data_content += f"\t{self.username_field} = serializers.{'EmailField()' if is_email else 'CharField()'}\n"
        data_content += f"\tpassword = serializers.CharField()\n\n\n"

        data_content += f"class RegisterSerializer(serializers.Serializer):\n"
        data_content += f"\temail = serializers.EmailField()\n"
        data_content += f"\tusername = serializers.CharField()\n"

        fields = self.project_auth.properties["fields"]

        for field_data in fields:
            field_attrs = field_data.get("field_properties", None)
            attrs_string = ""

            for key, value in field_attrs.items():
                if key != "null":
                    continue
                attrs_string += f"required={not value}"
            data_content += f"\t{field_data['name']} = serializers.{field_data['field_type']}({attrs_string})\n"

        data_content += f"\tpassword = serializers.CharField()\n\n\n"

        data_content += f"class RefreshSerializer(serializers.Serializer):\n"
        data_content += f"\trefresh = serializers.CharField()\n\n\n"

        data_content += f"class {self.custom_username}Serializer(serializers.ModelSerializer):\n\n"
        data_content += f"\tclass Meta:\n"
        data_content += f"\t\tmodel = {self.custom_username}\n"
        data_content += f"\t\texclude = ('password', )\n\n\n"

        write_to_file(self.app_path, "serializers.py", data_content)

    def create_views(self):
        # define imports
        data_content = f"from .models import Jwt, {self.custom_username}\n"
        data_content += f"from .serializers import LoginSerializer, RegisterSerializer, RefreshSerializer, {self.custom_username}Serializer\n"
        data_content += f"from django.contrib.auth import authenticate\n"
        data_content += f"from rest_framework.response import Response\n"
        data_content += f"from rest_framework.views import APIView\n"
        data_content += f"from .utils import get_access_token, get_refresh_token, verify_token\n"
        data_content += f"from .methods import IsAuthenticatedCustom\n"
        data_content += f"from rest_framework.viewsets import ModelViewSet\n\n\n"

        # create login view
        data_content += f"class LoginView(APIView):\n"
        data_content += f"\tserializer_class = LoginSerializer\n\n"

        data_content += f"\tdef post(self, request):\n"
        data_content += f"\t\tserializer = self.serializer_class(data=request.data)\n"
        data_content += f"\t\tserializer.is_valid(raise_exception=True)\n\n"

        data_content += f"\t\tuser = authenticate({self.username_field}=serializer.validated['{self.username_field}'], password=serializer.validated['password'])\n\n"

        data_content += f"\t\tJwt.objects.filter(user_id=user.id).delete()\n\n"

        data_content += "\t\taccess = get_access_token({'user_id': user.id})\n"
        data_content += "\t\trefresh = get_refresh_token()\n\n"

        data_content += f"\t\tJwt.objects.create(user_id=user.id, access=access.decode(), refresh=refresh.decode())\n\n"

        data_content += "\t\treturn Response({'access': access, 'refresh': refresh})\n\n\n"

        # create register view
        data_content += f"class RegisterView(APIView):\n"
        data_content += f"\tserializer_class = RegisterSerializer\n\n"

        data_content += f"\tdef post(self, request):\n"
        data_content += f"\t\tserializer = self.serializer_class(data=request.data)\n"
        data_content += f"\t\tserializer.is_valid(raise_exception=True)\n\n"

        data_content += f"\t\t{self.username_field} = serializer.validated_data.pop('{self.username_field}')\n\n"

        data_content += f"\t\t{self.custom_username}.objects.create_user({self.username_field}={self.username_field}, **serializer.validated_data)\n\n"

        data_content += "\t\treturn Response({'success': 'User created.'}, status=201)\n\n\n"

        # create refresh view
        data_content += f"class RefreshView(APIView):\n"
        data_content += f"\tserializer_class = RefreshSerializer\n\n"

        data_content += f"\tdef post(self, request):\n"
        data_content += f"\t\tserializer = self.serializer_class(data=request.data)\n"
        data_content += f"\t\tserializer.is_valid(raise_exception=True)\n\n"

        data_content += f"\t\ttry:\n"
        data_content += f"\t\t\tactive_jwt = Jwt.objects.get(refresh=serializer.validated_data['refresh'])\n"
        data_content += f"\t\texcept Jwt.DoesNotExist:\n"
        data_content += "\t\t\treturn Response({'error': 'refresh token not found'}, status='400')\n\n"

        data_content += f"\t\tif not verify_token(serializer.validated_data['refresh']):\n"
        data_content += "\t\t\treturn Response({'error': 'Token is invalid or has expired'}, status='400')\n\n"

        data_content += "\t\taccess = get_access_token({'user_id': active_jwt.user.id})\n"
        data_content += "\t\trefresh = get_refresh_token()\n\n"

        data_content += "\t\tactive_jwt.access = access.decode()\n"
        data_content += "\t\tactive_jwt.refresh = refresh.decode()\n"
        data_content += "\t\tactive_jwt.save()\n\n"

        data_content += "\t\treturn Response({'success': 'User created.'}, status=201)\n\n\n"

        # create me view
        data_content += f"class MeView(APIView):\n"
        data_content += f"\tpermission_classes = (IsAuthenticatedCustom, )\n"
        data_content += f"\tserializer_class = {self.custom_username}Serializer\n\n"

        data_content += f"\tdef get(self, request):\n"
        data_content += "\t\treturn Response(self.serializer_class(request.user).data)\n\n\n"

        # create logout view
        data_content += f"class LogoutView(APIView):\n"
        data_content += f"\tpermission_classes = (IsAuthenticatedCustom, )\n\n"

        data_content += f"\tdef get(self, request):\n"
        data_content += "\t\tuser_id = request.user.id\n"
        data_content += "\t\tJwt.objects.filter(user_id=user_id).delete()\n"
        data_content += "\t\treturn Response('logged out successfully', status=200)\n"

        write_to_file(self.app_path, "views.py", data_content)

    def create_urls(self):
        # define imports
        data_content = "from django.urls import path\n"
        data_content += f"from .views import LoginView, RegisterView, RefreshView, MeView, LogoutView\n\n"

        data_content += f"urlpatterns = [\n"
        data_content += f"\tpath('login', LoginView.as_view()),\n"
        data_content += f"\tpath('register', RegisterView.as_view()),\n"
        data_content += f"\tpath('refresh', RefreshView.as_view()),\n"
        data_content += f"\tpath('me', MeView.as_view()),\n"
        data_content += f"\tpath('logout', LogoutView.as_view())\n"
        data_content += f"]\n"

        write_to_file(self.app_path, "urls.py", data_content)

    def clean_up(self):
        if self.project.has_migration:
            self.delete_exist_db()
        # delete AuthDirectory is exist
        try:
            DirectoryManager.delete_directory(self.app_path)
            self.project.project_setting.properties["INSTALLED_APPS"]["items"].remove(
                self.auth_app_name)
            del self.project.project_setting.properties['AUTH_USER_MODEL']
            self.project.project_setting.save()
        except:
            pass

    def finalize_process(self):
        # write settings file
        settings_c = WriteSettings(self.project)
        # update project settings
        if not self.isDel:
            if self.auth_app_name not in self.project.project_setting.properties["INSTALLED_APPS"]["items"]:
                self.project.project_setting.properties["INSTALLED_APPS"]["items"].append(
                    self.auth_app_name)
                self.project.project_setting.properties["AUTH_USER_MODEL"] = {
                    "value": f"{self.auth_app_name}.{self.custom_username}",
                    "is_string": True
                }

        if self.project.project_setting.properties.get("REST_FRAMEWORK", None):
            props = self.project.project_setting.properties["REST_FRAMEWORK"]["properties"]
            new_props = []
            for i in props:
                if i["key"] == "DEFAULT_AUTHENTICATION_CLASSES":
                    continue
                new_props.append(i)
                
            self.project.project_setting.properties["REST_FRAMEWORK"]['properties'] = new_props
            self.project.project_setting.save()

            if not self.isDel:                    
                self.project.project_setting.properties["REST_FRAMEWORK"]['properties'].append(
                    {
                        "key": "DEFAULT_AUTHENTICATION_CLASSES",
                        "values": [
                            f"{self.auth_app_name}.methods.{self.project_auth.default_auth}"
                        ]
                    }
                )
        else:
            if not self.isDel:
                if self.project_auth.default_auth:
                    self.project.project_setting.properties["REST_FRAMEWORK"] = {
                        "properties": [
                            {
                                "key": "DEFAULT_AUTHENTICATION_CLASSES",
                                "values": [
                                    f"{self.auth_app_name}.methods.{self.project_auth.default_auth}"
                                ]
                            }
                        ]
                    }

        self.project.project_setting.save()
        settings_c.update_setting(self.project.project_setting.properties)

        # write project url
        url_c = WriteProjectUrl(self.project)
        url_c.write_url()

        # update migration
        self.run_migration()
        self.project.has_migration = True
        self.project.save()
