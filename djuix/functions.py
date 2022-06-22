from project_controller.models import SettingHeader, SettingValue
from .helper import Helper
from controllers.directory_controller import DirectoryManager
from abstractions.enums import Enums


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
  
def create_settings(project_name, project_id):
    # add os import for settings
    SettingHeader.objects.update_or_create(value="import os", project_id=project_id)

    settings_contents = [
        {
            "name": Enums.BASE_DIR,
            "value": 'os.path.dirname(os.path.dirname(os.path.abspath(__file__)))'
        },
        {
            "name": Enums.SECRET_KEY,
            "value": f"'{Helper.generate_random_string(30)}'"
        },
        {
            "name": Enums.DEBUG,
            "value": "True"
        },
        {
            "name": Enums.ALLOWED_HOSTS,
            "value": "['*']"
        },
        {
            "name": Enums.INSTALLED_APPS,
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
            "name": Enums.MIDDLEWARE,
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
            "name": Enums.ROOT_URLCONF,
            "value": f"'{project_name}.urls'"
        },
        {
            "name": Enums.WSGI_APPLICATION,
            "value": f"'{project_name}.wsgi.application'"
        },
        {
            "name": Enums.TEMPLATES,
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
            "name": Enums.DATABASES,
            "value": """{
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}"""
        },
        {
            "name": Enums.AUTH_PASSWORD_VALIDATORS,
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
            "name": Enums.LANGUAGE_CODE,
            "value": "'en-us'"
        },
        {
            "name": Enums.TIME_ZONE,
            "value": "'UTC'"
        },
        {
            "name": Enums.USE_I18N,
            "value": 'True'
        },
        {
            "name": Enums.USE_L10N,
            "value": 'True'
        },
        {
            "name": Enums.USE_TZ,
            "value": 'True'
        },
        {
            "name": Enums.CORS_ORIGIN_ALLOW_ALL,
            "value": 'True'
        },
        {
            "name": Enums.CORS_ALLOW_HEADERS,
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
            "name": Enums.CORS_ALLOW_CREDENTIALS,
            "value": "False"
        },
        {
            "name": Enums.CORS_ALLOW_METHODS,
            "value": "('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')"
        },
        {
            "name": Enums.STATIC_URL,
            "value": "'/static/'"
        },
    ]

    SettingValue.objects.bulk_create(
        [SettingValue(project_id=project_id, **data) for data in settings_contents])
    
def write_to_file(path_data, file_name, content):
    try:
        directory_manager = DirectoryManager(path_data)
        file_data = directory_manager.create_file(file_name)
        directory_manager.write_file(file_data, content)
        return True
    except Exception as e:
        print(e)
        return False
