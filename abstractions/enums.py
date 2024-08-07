class Enums:
    ALLOWED_HOSTS = "ALLOWED_HOSTS"
    AUTH_PASSWORD_VALIDATORS = "AUTH_PASSWORD_VALIDATORS"
    BASE_DIR = "BASE_DIR"
    CORS_ALLOW_CREDENTIALS = "CORS_ALLOW_CREDENTIALS"
    CORS_ALLOW_HEADERS = "CORS_ALLOW_HEADERS"
    CORS_ALLOW_METHODS = "CORS_ALLOW_METHODS"
    CORS_ORIGIN_ALLOW_ALL = "CORS_ORIGIN_ALLOW_ALL"
    DATABASES = "DATABASES"
    DEBUG = "DEBUG"
    INSTALLED_APPS = "INSTALLED_APPS"
    LANGUAGE_CODE = "LANGUAGE_CODE"
    MIDDLEWARE = "MIDDLEWARE"
    ROOT_URLCONF = "ROOT_URLCONF"
    SECRET_KEY = "SECRET_KEY"
    STATIC_URL = "STATIC_URL"
    TEMPLATES = "TEMPLATES"
    TIME_ZONE = "TIME_ZONE"
    USE_I18N = "USE_I18N"
    USE_L10N = "USE_L10N"
    USE_TZ = "USE_TZ"
    WSGI_APPLICATION = "WSGI_APPLICATION"
    
    
class ModelFieldTypes:
    CharField = "CharField"
    TextField = "TextField" 
    DateTimeField = "DateTimeField"
    FileField = "FileField"
    ImageField = "ImageField"
    JSONField = "JSONField"
    ForeignKey = "ForeignKey"
    OneToOneField = "OneToOneField"
    ManyToManyField = "ManyToManyField"
    EmailField = "EmailField"
    SlugField = "SlugField"
    UUIDField = "UUIDField"
    BooleanField = "BooleanField"
    FloatField = "FloatField"
    IntegerField = "IntegerField"
    

class SerializerFieldTypes:
    CharField = "CharField"
    EmailField = "EmailField"
    FloatField = "FloatField"
    IntegerField = "IntegerField"
    SerializerMethodField = "SerializerMethodField"