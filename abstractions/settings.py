import os


# this will server as the basic abstraction of the default content in a just generated django project
class SettingsAbstraction:
    file_name = "settings.py"
    OS_IMPORT = 'import os'
    BASE_DIR = "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))"
    SECRET_KEY = "'s_b=5%2n=!(dehix7vlv*r3*si)+kjob3ev=6k%kknv%sd#hk2'"
    DEBUG = True
    ALLOWED_HOSTS = "[]"
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
    ]
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]
    ROOT_URLCONF = "'djuix.urls'"
    TEMPLATES = """[
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
    WSGI_APPLICATION = "'djuix.wsgi.application'"
    DATABASES = """{
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }"""

    AUTH_PASSWORD_VALIDATORS = """[
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

    LANGUAGE_CODE = "'en-us'"

    TIME_ZONE = "'UTC'"

    USE_I18N = True

    USE_L10N = True

    USE_TZ = True

    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_HEADERS = (
        'x-requested-with',
        'content-type',
        'accept',
        'origin',
        'authorization',
        'accept-encoding',
        'x-csrftoken',
        'access-control-allow-origin',
        'content-disposition'
    )
    CORS_ALLOW_CREDENTIALS = False
    CORS_ALLOW_METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS')
    default_storage = "STATIC_URL = '/static/'"

    def get_template(self):
        template_str = f"{self.OS_IMPORT}\n\n"
        template_str += f"BASE_DIR = {self.BASE_DIR}\n\n"
        template_str += f"SECRET_KEY = {self.SECRET_KEY}\n\n"
        template_str += f"DEBUG = {self.DEBUG}\n\n"
        template_str += f"INSTALLED_APPS = {self.stringify_list(self.INSTALLED_APPS)}\n\n"
        template_str += f"ALLOWED_HOSTS = {self.ALLOWED_HOSTS}\n\n"
        template_str += f"MIDDLEWARE = {self.stringify_list(self.MIDDLEWARE)}\n\n"
        template_str += f"ROOT_URLCONF = {self.ROOT_URLCONF}\n\n"
        template_str += f"TEMPLATES = {self.TEMPLATES}\n\n"
        template_str += f"WSGI_APPLICATION = {self.WSGI_APPLICATION}\n\n"
        template_str += f"DATABASES = {self.DATABASES}\n\n"
        template_str += f"AUTH_PASSWORD_VALIDATORS = {self.AUTH_PASSWORD_VALIDATORS}\n\n"
        template_str += f"LANGUAGE_CODE = {self.LANGUAGE_CODE}\n\n"
        template_str += f"TIME_ZONE = {self.TIME_ZONE}\n\n"
        template_str += f"USE_I18N = {self.USE_I18N}\n\n"
        template_str += f"USE_L10N = {self.USE_L10N}\n\n"
        template_str += f"USE_TZ = {self.USE_TZ}\n\n"
        template_str += f"CORS_ORIGIN_ALLOW_ALL = {self.CORS_ORIGIN_ALLOW_ALL}\n\n"
        template_str += f"CORS_ALLOW_HEADERS = {self.stringify_list(self.CORS_ALLOW_HEADERS)}\n\n"
        template_str += f"CORS_ALLOW_CREDENTIALS = {self.CORS_ALLOW_CREDENTIALS}\n\n"
        template_str += f"CORS_ALLOW_METHODS = {self.CORS_ALLOW_METHODS}\n\n"
        template_str += f"{self.default_storage}\n\n"

        return template_str

    @staticmethod
    def stringify_list(list_content):
        string_form = "[\n"
        for item in list_content:
            string_form += f"\t'{item}',\n"
        return string_form + "]"

    def set_security_key(self, new_key):
        self.SECRET_KEY = new_key

    def set_debug(self, status):
        self.DEBUG = status

    def set_allowed_host(self, host_list):
        self.ALLOWED_HOSTS = host_list

    def set_installed_app(self, app_list):
        self.INSTALLED_APPS.extend(app_list)

    def set_middlewares(self, middleware_list):
        self.MIDDLEWARE = middleware_list

    def set_root_urlconf(self, new_root_name):
        self.ROOT_URLCONF = f"'{new_root_name}.urls'"

    def set_templates(self, new_template_list):
        self.TEMPLATES = new_template_list

    def set_storage(self, storage_info):
        self.default_storage = storage_info

    def set_wsgi_application(self, new_wsgi_name):
        self.WSGI_APPLICATION = f"'{new_wsgi_name}.wsgi.application'"

    def set_database(self, new_database):
        self.DATABASES = new_database

    def set_auth_password_validators(self, auth_password_validator_list):
        self.AUTH_PASSWORD_VALIDATORS = auth_password_validator_list

    def set_language_code(self, new_language_code):
        self.LANGUAGE_CODE = new_language_code

    def set_time_zone(self, new_time_zone):
        self.TIME_ZONE = new_time_zone

    def set_USE_I18N(self, new_USE_I18N):
        self.USE_I18N = new_USE_I18N

    def set_USE_TZ(self, new_USE_TZ):
        self.USE_TZ = new_USE_TZ

    def set_USE_L10N(self, new_USE_L10N):
        self.USE_L10N = new_USE_L10N

    def write_to_settings(self, path_to_settings):
        full_path = path_to_settings + self.file_name
        settings_file = open(full_path, "w")
        settings_file.write(self.get_template())
        settings_file.close()
        return True
