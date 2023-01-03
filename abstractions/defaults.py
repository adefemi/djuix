from calendar import c


DEFAULT_PROJECT_DIR="/djuix-files"
PROJECT_TEMPLATES = [
    {
        "name": "blog",
        "title": "Blog",
        "description": "Generates a new blog project"
    }
]
PACKAGE_LIST = [
    {
        "name": "django",
        "version": "django==3.1.4"
    }, 
    {
        "name": "cors",
        "version": "django-cors-headers==3.6.0"
    },
    {
        "name": "rest_framework",
        "version": "djangorestframework==3.13.1"
    },
    {
        "name": "pillow",
        "version": "Pillow==9.2.0"
    }
]

OPTIONAL_PACKAGES = {
    "boto": {
        "name": "boto",
        "version": "boto3==1.26.37"
    },
    "django_storages": {
        "name": "django_storages",
        "version": "django-storages==1.10"
    },
    "cloudinary": {
        "name": "cloudinary",
        "version": "cloudinary==1.30.0"
    },
    "django_cloudinary": {
        "name": "django-cloudinary-storage",
        "version": "django-cloudinary-storage==0.3.0"
    },
    "psycopg2": {
        "name": "psycopg2-binary",
        "version": "psycopg2-binary==2.9.5"
    },
    "pyJwt": {
        "name": "PyJWT",
        "version": "PyJWT==2.6.0"
    }
}

SETTINGS_INFO = [
    {
        "name": "ENVIRONMENT SETUP",
        "tag": "ENVIRONMENT",
        "properties": [
            {
                "name": "Environment",
                "key": "DEBUG",
                "options": {
                    "Production": "False",
                    "Debug": "True",
                }
            },
            # {
            #     "name": "Secret Key",
            #     "key": "SECRET_KEY",
            #     "value": "",
            #     "is_secure": True,
            # },
            # {
            #     "name": "Allowed Hosts",
            #     "key": "ALLOWED_HOSTS",
            #     "value": "",
            #     "help_text": "Specify your allowed hosts separated with a comma"
            # },
            {
                "name": "Language",
                "key": "LANGUAGE_CODE",
                "options": {
                    "en-us": "en-us",
                },
                "is_required": True,
            },
            {
                "name": "Timezone",
                "key": "TIME_ZONE",
                "options": {
                    "UTC": "'UTC'",
                },
                "is_required": True,
            },
            {
                "name": "USE TZ",
                "key": "USE_TZ",
                "value": "",
                "is_boolean": True,
                "is_required": True,
            },
        ]
    },
    {
        "name": "DATABASE",
        "tag": "DATABASE",
        "properties": [
            {
                "name": "Engine",
                "key": "engine",
                "options": {
                    "Postgres": "postgres",
                    "Sqlite": "sqlite",
                }
            },
        ],
        "context": {
            "postgres": [
                {
                    "name": "DB Name",
                    "key": "DB_NAME",
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "DB User",
                    "key": "DB_USER",
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "DB Host",
                    "key": "DB_HOST",
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "DB Port",
                    "key": "DB_PORT",
                    "value": "",
                    "is_number": True,
                    "is_required": True,
                },
                {
                    "name": "DB Password",
                    "key": "DB_PASSWORD",
                    "is_secure": True,
                    "value": "",
                    "is_required": True,
                },
            ]
        }
    },
    {
        "name": "FILE STORAGE",
        "tag": "STORAGE",
        "properties": [
            {
                "name": "Engine",
                "key": "engine",
                "options": {
                    "None": "",
                    "AWS": "aws",
                    "Cloudinary": "cloudinary",
                }
            },
        ],
        "context": {
            "aws": [
                {
                    "name": "Access key ID",
                    "key": "AWS_ACCESS_KEY_ID",
                    "is_secure": True,
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "Secret key ID",
                    "key": "AWS_SECRET_ACCESS_KEY",
                    "is_secure": True,
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "Storage bucket name",
                    "key": "AWS_STORAGE_BUCKET_NAME",
                    "value": "",
                    "is_required": True,
                },
            ],
            "cloudinary": [
                {
                    "name": "Cloud name",
                    "key": "CLOUD_NAME",
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "Api key",
                    "key": "API_KEY",
                    "is_secure": True,
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "Api secret",
                    "key": "API_SECRET",
                    "is_secure": True,
                    "value": "",
                    "is_required": True,
                },
            ]
        }
    },
    {
        "name": "EMAIL SETUP",
        "tag": "EMAIL",
        "properties": [
            {
                "name": "Engine",
                "key": "engine",
                "options": {
                    "None": "",
                    "Set credentials": "email",
                }
            },
        ],
        "context": {
            "email": [
                {
                    "name": "Host",
                    "key": "HOST",
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "Host User",
                    "key": "HOST_USER",
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "Password",
                    "key": "PASSWORD",
                    "value": "",
                    "is_secure": True,
                    "is_required": True,
                },
                {
                    "name": "Port",
                    "key": "PORT",
                    "value": "",
                    "is_number": True,
                    "is_required": True,
                },
                {
                    "name": "Default from email",
                    "key": "DEFAULT_FROM_EMAIL",
                    "value": "",
                    "is_required": True,
                },
                {
                    "name": "USE TLS",
                    "key": "USE_TLS",
                    "value": "",
                    "is_boolean": True,
                    "is_required": True,
                },
            ]
        }
    }
]

common_relation_reference = {
            "related_model_name": {
                "type": "options",
                "name": "Model Reference",
                "instruction": "fetch_model_references",
                "placeholder": "Select a model reference"
            },
            "related_name": {
                "type": "string",
                "name": "Related Name",
                "optional": True,
                "placeholder": "This is useful for reverse targetting"
            },
            "on_delete": {
                "type": "options",
                "name": "On Delete Reference",
                "placeholder": "Decide what happens when a model reference is deleted",
                "options": {
                    "models.CASCADE": "Delete record",
                    "models.SET_NULL": "Keep record",
                }
            }
        }

common_file_reference = {
            "upload_to": {
                "type": "string",
                "name": "Upload to path",
                "placeholder": "folder to upload to on your file storage",
                "optional": True,
            }
        }

FIELD_TYPES = [
        "CharField",
        "TextField",
        "DateTimeField", 
        "FileField",
        "ImageField",
        "JSONField",
        "ForeignKey",
        "OneToOneField",
        "ManyToManyField",
        "EmailField", 
        "SlugField",
        "UUIDField", 
        "BooleanField", 
        "FloatField",
        "IntegerField",
    ]

MODEL_REQUIREMENT = {
    "types": FIELD_TYPES,
    "options_by_type": {
        "CharField": {
            "max_length": {
                "type": "integer",
                "name": "Maximum length",
                "placeholder": "The maximum length of the field"
            }
        },
        "FileField": common_file_reference,
        "ImageField": common_file_reference,
        "ForeignKey": common_relation_reference,
        "OneToOneField": common_relation_reference,
        "ManyToManyField": {x: common_relation_reference[x] for x in common_relation_reference if x not in ["on_delete"]},
        "SlugField": {
            "field_reference": {
                "type": "options", 
                "name": "Field Reference",
                "instruction": "get_field_references"
            }
        }
    },
    "defaults": {
        "help_text": {
            "type": "string",
            "name": "Description",
            "optional": True,
            "placeholder": "Describe what the field does if its not obvious"
        },
        "default": {
            "type": "string",
            "optional": True,
            "name": "Default Content",
            "placeholder": "What the field holds by default"
        },
        "unique": {
            "type": "boolean",
            "name": "Unique"
        },
        "null": {
            "type": "boolean",
            "name": "null"
        },
        "blank": {
            "type": "boolean",
            "name": "blank"
        }
    }
}

SERIALIZER_FIELD_TYPES = []

for i in FIELD_TYPES:
    if i in ["ForeignKey", "OneToOneField", "ManyToManyField"]:
        continue
    SERIALIZER_FIELD_TYPES.append(i)
    
SERIALIZER_FIELD_TYPES.append("RelatedField")

SERIALIZER_REQUIREMENT = {
    "types": SERIALIZER_FIELD_TYPES,
    "options_by_type": {
        "RelatedField": {
            "related_serializer_name": {
                "type": "options",
                "name": "Serializer Reference",
                "instruction": "fetch_serializer_references",
                "placeholder": "Select a serializer reference"
            },
        }
    },
    "defaults": {
        "read_only": {
            "type": "boolean",
            "name": "is_read_only"
        },
        "write_only": {
            "type": "boolean",
            "name": "is_write_only"
        },
        "required": {
            "type": "boolean",
            "name": "not_required"
        },
        "many": {
            "type": "boolean",
            "name": "has_many_outputs"
        },
    }
}

AUTH_URLS = [
    {
        "name": "Login User",
        "link": "/auth-path/login",
        "allowed_methods": ["POST"],
        "description": "Login to the application using your 'Username field' and 'Password'"
    },
    {
        "name": "Register User",
        "link": "/auth-path/register",
        "allowed_methods": ["POST"],
        "description": "Sign up to the application, you will need to provide your 'Email, Username, Password and Extra Required field provided during Auth setup.'"
    },
    {
        "name": "Refresh Token",
        "link": "/auth-path/refresh",
        "allowed_methods": ["POST"],
        "description": "Get a new access token by providing the current Refresh token"
    },
    {
        "name": "Active User",
        "link": "/auth-path/me",
        "allowed_methods": ["GET"],
        "description": "Get logged in user information. You must provide the access token in the AUTHORIZARION header field"
    },
    {
        "name": "Logout User",
        "link": "/auth-path/logout",
        "allowed_methods": ["GET"],
        "description": "Invalidate the access token and logout the user. You must provide the access token in the AUTHORIZARION header field"
    },
]

auth_app_name = "AuthController"
app_email_name = "Djuix.io Team"
support_mail = "admin@djuix.io"