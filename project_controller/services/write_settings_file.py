from app_controller.services.writer_main import WriterMain
from djuix.functions import write_to_file
from project_controller.models import ProjectSettings


class WriteSettings(WriterMain):
    project = None
    content_data = ""
    settings_object = None
    
    def __init__(self, project):
        super().__init__(None)
        self.project = project
        self.set_settings_obj()
        
    def create_setting(self):
        self.save_properties_to_setting()
        self.write_setting()
        
    def update_setting(self, obj):
        self.settings_object = obj
        self.write_setting()
        
    def write_setting(self):
        print("writing project setting...")
        
        self.check_for_import()
        if self.content_data:
            self.content_data += "\n\n"
        
        for k,v in self.settings_object.items():
            
            if k == "TEMPLATES":
                self.set_template_key(v)
                continue
            
            if k == "DATABASES":
                self.set_database_key(v["properties"])
                continue
        
            value = ""
            if v.get('value', None) is not None:
                value = v['value']
                if v.get("is_string", False):
                    value = f"'{value}'"
            elif v.get("items", None) is not None:
                value = "[\n"
                for i in v["items"]:
                    if v.get("is_string", False):
                        i = f"'{i}'"
                    value += f"\t{i},\n"
                    
                value += "]"
            self.content_data += f"\n{k} = {value}\n"
        
        path_data = f"{self.project.project_path}/{self.project.formatted_name}/{self.project.formatted_name}/"
        
        write_to_file(path_data, 'settings.py', self.content_data)
        
    def set_template_key(self, props):
        self.content_data += "\nTEMPLATES = [\n\t{\n"
        self.content_data += f"\t\t'BACKEND': '{props['BACKEND']}',\n"
        self.content_data += f"\t\t'DIRS': {props['DIRS']},\n"
        self.content_data += f"\t\t'APP_DIRS': {props['APP_DIRS']},\n"
        self.content_data += "\t\t'OPTIONS': {\n"
        
        for i in props["options"]:
            self.content_data += f"\t\t\t'{i['name']}': [\n"
            for j in i['items']:
                self.content_data += f"\t\t\t\t'{j}',\n"
            self.content_data += f"\t\t\t]\n"
        
        self.content_data += "\t\t}\n"
        self.content_data += "\t}\n"
        self.content_data += "]\n"
        
    def set_database_key(self, props):
        self.content_data += "\nDATABASES = {\n\t'default': {\n"
        for k,v in props.items():
            if k == "key": continue
            
            if k == "PORT":
                v = f"{v}"
            else:
                v = f'"{v}"'
            self.content_data += f"\t\t'{k}': {v},\n"
        self.content_data += "\t}\n}\n"
        
    def check_for_import(self):
        print("writing view imports")
        import_obj = {}
        
        for k,v in self.settings_object.items():
            if v.get('imports', False):
                import_key = v["imports"]
                
                key = "generic" if not import_key["parent"] else import_key["parent"]
            
                if not import_obj.get(key, None):
                    import_obj[key] = []
                    
                if import_key["name"] not in import_obj[key]:
                    import_obj[key].append(import_key["name"])
                    
        self.format_import(import_obj)
        
    def set_settings_obj(self):
        self.settings_object = {
            "BASE_DIR": {
                "value": "os.path.dirname(os.path.dirname(os.path.abspath(__file__)))",
                "imports": {
                    "parent": None,
                    "name": "os"
                }
            },
            "SECRET_KEY": {
                "value": "s_b=5%2n=!(dehix7vlv*r3*si)+kjob3ev=6k%kknv%sd#hk2",
                "is_string": True
            },
            "DEBUG": {
                "value": "True"
            },
            "ALLOWED_HOSTS": {
                "value": "['*']"
            },
            "INSTALLED_APPS": {
                "items": [
                    "django.contrib.admin",
                    "django.contrib.auth",
                    "django.contrib.contenttypes",
                    "django.contrib.sessions",
                    "django.contrib.messages",
                    "django.contrib.staticfiles",
                ],
                "is_string": True
            },
            "MIDDLEWARE": {
                "items": [
                    "django.middleware.security.SecurityMiddleware",
                    "django.contrib.sessions.middleware.SessionMiddleware",
                    "django.middleware.common.CommonMiddleware",
                    "django.middleware.csrf.CsrfViewMiddleware",
                    "django.contrib.auth.middleware.AuthenticationMiddleware",
                    "django.contrib.messages.middleware.MessageMiddleware",
                    "django.middleware.clickjacking.XFrameOptionsMiddleware",
                ],
                "is_string": True
            },
            "ROOT_URLCONF": {
                "value": f"{self.project.formatted_name}.urls",
                "is_string": True
            },
            "TEMPLATES": {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": '[]',
                "APP_DIRS": 'True',
                "options": [
                    {
                        'name': "context_processors",
                        'items': [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ]
                    }
                ]
            },
            "WSGI_APPLICATION": {
                "value": f"{self.project.formatted_name}.wsgi.application",
                "is_string": True
            },
            "DATABASES": {
                "properties": {
                    "key": "sqlite",
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": "os.path.join(BASE_DIR, 'db.sqlite3')",
                },
                "imports": {
                    "parent": None,
                    "name": "os"
                }
            },
            "AUTH_PASSWORD_VALIDATORS": {
                "items": [
                    "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
                    "django.contrib.auth.password_validation.MinimumLengthValidator",
                    "django.contrib.auth.password_validation.CommonPasswordValidator",
                    "django.contrib.auth.password_validation.NumericPasswordValidator",
                ],
                "is_string": True
            },
            "LANGUAGE_CODE": {
                'value': "en-us",
                "is_string": True
            },
            "TIME_ZONE": {
                'value': "UTC",
                "is_string": True
            },
            "USE_I18N": {
                "value": 'True'
            },
            "USE_L10N": {
                "value": 'True'
            },
            "USE_TZ": {
                "value": 'True'
            },
            "STATIC_URL": {
                "value": "/static/",
                "is_string": True
            }
        }
                
    def save_properties_to_setting(self):
        ProjectSettings.objects.create(project_id=self.project.id, properties=self.settings_object)
        
    def update_package_on_setting(self, package_list):
        
        for i in package_list:
            if i["name"] == "rest_framework":
                self.settings_object["INSTALLED_APPS"]["items"].append("rest_framework")
            if i["name"] == "cors":
                self.settings_object["INSTALLED_APPS"]["items"].append("corsheaders")
                self.settings_object["CORS_ORIGIN_ALLOW_ALL"] = {
                    "value": 'True'
                }
                self.settings_object["CORS_ALLOW_CREDENTIALS"] = {
                    "value": 'False'
                }
                self.settings_object["CORS_ALLOW_METHODS"] = {
                    "items": ["'GET'", "'POST'", "'PUT'", "'PATCH'", "'DELETE'", "'OPTIONS'"]
                }
                self.settings_object["MIDDLEWARE"]["items"].insert(2, "corsheaders.middleware.CorsMiddleware")
                self.settings_object["CORS_ALLOW_HEADERS"] = {
                    "items": [
                        "'x-requested-with'",
                        "'content-type'",
                        "'accept'",
                        "'origin'",
                        "'authorization'",
                        "'accept-encoding'",
                        "'x-csrftoken'",
                        "'access-control-allow-origin'",
                        "'content-disposition'"
                    ]
                }
                
                
        