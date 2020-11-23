from project_controller.models import SettingHeader, SettingValue
from .helper import Helper
from controllers.directory_controller import DirectoryManager


# update settings file
def update_settings(settings_path, project_id):
    settings_template = ""
    setting_headers = SettingHeader.objects.filter(project_id=project_id)
    if setting_headers:
        for header in setting_headers:
            settings_template += f"{header.value}\n"
        settings_template += "\n\n"

    setting_values = SettingValue.objects.filter(project_id=project_id)
    if setting_values:
        for value in setting_values:
            settings_template += f"{value.name} = {value.value}\n\n"

    directory_manager = DirectoryManager(settings_path)
    file_data = directory_manager.create_file("settings.py")
    directory_manager.write_file(file_data, settings_template)


class WriteToSerializer:

    def __init__(self, app_data, serializer_data):
        self.app_data = app_data
        self.serializer_data = serializer_data

    def write_to_serializer(self):
        content_data = "from rest_framework import serializers\n"

        for active_serializer in self.serializer_data:
            try:
                content_data += f"from .models import {active_serializer.model_relation.name}\n"
            except Exception:
                pass
        content_data += "\n\n"

        for active_serializer in self.serializer_data:
            model_name = None
            try:
                model_name = active_serializer.model_relation.name
            except Exception:
                pass

            content_data += f"class {active_serializer.name}({'serializers.Serializer' if not model_name else 'serializers.ModelSerializer'}):\n"
            fields = active_serializer.serializer_fields.all()

            for field_data in fields:

                content_data += f"\t{field_data.name} = serializers.{field_data.field_type}("
                content_data = self.check_general(field_data, content_data)

                content_data = content_data[:-2]
                content_data += ")\n"
            content_data += "\n"

            if model_name:
                content_data += "\tclass Meta:\n"
                content_data += "\t\tfields='__all__'\n"
                content_data += f"\t\tmodel={model_name}\n"
                content_data += "\n\n"

        try:
            serializer_path = f"{self.app_data.project.project_path}{self.app_data.project.name}/{self.app_data.name}/"
            directory_manager = DirectoryManager(serializer_path)
            file_data = directory_manager.create_file("serializers.py")
            directory_manager.write_file(file_data, content_data)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def check_general(field_data, content_data):
        if not field_data.is_required:
            content_data += "required=False, "
        if field_data.is_write_only:
            content_data += "write_only=True, "
        if field_data.is_read_only:
            content_data += "read_only=True, "
        if field_data.is_many:
            content_data += "many=True, "
        return content_data


class WriteToModel:

    def __init__(self, app_data, models_data):
        self.app_data = app_data
        self.models_data = models_data

    def write_model(self):
        # define the base structure
        content_data = "from django.db import models\n\n\n"

        for model_data in self.models_data:
            content_data += f"class {model_data.name}(models.Model):\n"
            fields = model_data.model_fields.all()

            for field_data in fields:

                content_data += f"\t{field_data.name} = models.{field_data.field_type}("
                content_data = self.check_general(field_data, content_data)
                if field_data.field_type == "CharField":
                    content_data = self.check_char(field_data, content_data)
                elif field_data.is_related:
                    content_data = self.check_related(field_data, content_data)
                elif field_data.field_type == "DateTimeField":
                    content_data = self.check_date(field_data, content_data)

                content_data = content_data[:-2]
                content_data += ")\n"
            content_data += "\n\n"

        try:
            model_path = f"{self.app_data.project.project_path}{self.app_data.project.name}/{self.app_data.name}/"
            directory_manager = DirectoryManager(model_path)
            file_data = directory_manager.create_file("models.py")
            directory_manager.write_file(file_data, content_data)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def check_general(field_data, content_data):
        if field_data.is_null:
            content_data += "null=True, "
        if field_data.is_blank:
            content_data += "blank=True, "
        if field_data.is_unique:
            content_data += "unique=True, "
        if field_data.default_value:
            content_data += f"default={field_data.default_value}, "
        if field_data.helper_text:
            content_data += f"help_text={field_data.helper_text}, "
        return content_data

    @staticmethod
    def check_char(field_data, content_data):
        if field_data.max_length:
            content_data += f"max_length={field_data.max_length}, "
        else:
            content_data += "max_length=255, "
        return content_data

    @staticmethod
    def check_related(field_data, content_data):
        content_data += f"'{field_data.related_model_name}', "
        content_data += f"related_name='{field_data.related_name_main}', "
        return content_data

    @staticmethod
    def check_date(field_data, content_data):
        if field_data.is_created_at:
            content_data += f"auto_now_add=True, "
        else:
            content_data += f"auto_now=True, "
        return content_data


def create_settings(project_name, project_id):
    # add os import for settings
    SettingHeader.objects.create(value="import os", project_id=project_id)

    settings_contents = [
        {
            "name": "BASE_DIR",
            "value": 'os.path.dirname(os.path.dirname(os.path.abspath(__file__)))'
        },
        {
            "name": "SECRET_KEY",
            "value": f"'{Helper.generate_random_string(30)}'"
        },
        {
            "name": "DEBUG",
            "value": "True"
        },
        {
            "name": "ALLOWED_HOSTS",
            "value": "['*']"
        },
        {
            "name": "INSTALLED_APPS",
            "value": """[
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
]"""
        },
        {
            "name": "MIDDLEWARE",
            "value": """[
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]"""
        },
        {
            "name": "ROOT_URLCONF",
            "value": f"'{project_name}.urls'"
        },
        {
            "name": "WSGI_APPLICATION",
            "value": f"'{project_name}.wsgi.application'"
        },
        {
            "name": "TEMPLATES",
            "value": """[
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]"""
        },
        {
            "name": "DATABASES",
            "value": """{
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}"""
        },
        {
            "name": "AUTH_PASSWORD_VALIDATORS",
            "value": """[
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]"""
        },
        {
            "name": "LANGUAGE_CODE",
            "value": "'en-us'"
        },
        {
            "name": "TIME_ZONE",
            "value": "'UTC'"
        },
        {
            "name": "USE_I18N",
            "value": 'True'
        },
        {
            "name": "USE_L10N",
            "value": 'True'
        },
        {
            "name": "USE_TZ",
            "value": 'True'
        },
        {
            "name": "CORS_ORIGIN_ALLOW_ALL",
            "value": 'True'
        },
        {
            "name": "CORS_ALLOW_HEADERS",
            "value": """(
    'x-requested-with',
    'content-type',
    'accept',
    'origin',
    'authorization',
    'accept-encoding',
    'x-csrftoken',
    'access-control-allow-origin',
    'content-disposition'
)"""
        },
        {
            "name": "CORS_ALLOW_CREDENTIALS",
            "value": "False"
        },
        {
            "name": "CORS_ALLOW_METHODS",
            "value": "('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')"
        },
        {
            "name": "STATIC_URL",
            "value": "'/static/'"
        },
    ]

    SettingValue.objects.bulk_create(
        [SettingValue(project_id=project_id, **data) for data in settings_contents])
