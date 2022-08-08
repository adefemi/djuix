from calendar import c


DEFAULT_PROJECT_DIR="/Users/adefemioseni/Desktop/djuix_test_projects"
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
        "version": "django==3.2.13"
    }, 
    {
        "name": "cors",
        "version": "django-cors-headers==3.12.0"
    },
    {
        "name": "rest_framework",
        "version": "djangorestframework==3.13.1"
    },
    {
        "name": "pillow",
        "version": "Pillow==9.1.1"
    }
]

SETTINGS_INFO = [
    {
        "name": "ENVIRONMENT SETUP",
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
                }
            },
            {
                "name": "Timezone",
                "key": "TIME_ZONE",
                "options": {
                    "UTC": "'UTC'",
                }
            },
            {
                "name": "USE TZ",
                "key": "USE_TZ",
                "value": "",
                "is_boolean": True
            },
        ]
    },
    {
        "name": "DATABASE",
        "tag": "DATABASES",
        "properties": [
            {
                "name": "Engine",
                "key": "ENGINE",
                "options": {
                    "Postgres": "postgres",
                    "Sqlite": "sqlite",
                }
            },
        ],
        "context": {
            "sqlite": None,
            "postgres": [
                {
                    "name": "name",
                    "key": "DB_NAME",
                    "value": ""
                },
                {
                    "name": "password",
                    "key": "DB_PASSWORD",
                    "is_secure": True,
                    "value": ""
                },
                {
                    "name": "host",
                    "key": "DB_HOST",
                    "value": "",
                },
                {
                    "name": "port",
                    "key": "DB_PORT",
                    "value": "",
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
                "key": "ENGINE",
                "options": {
                    "None": "none",
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
                },
                {
                    "name": "Secret key ID",
                    "key": "AWS_SECRET_ACCESS_KEY",
                    "is_secure": True,
                    "value": "",
                },
                {
                    "name": "Storage bucket name",
                    "key": "AWS_STORAGE_BUCKET_NAME",
                    "value": "",
                },
            ],
            "cloudinary": [
                {
                    "name": "Cloud name",
                    "key": "CLOUD_NAME",
                    "value": ""
                },
                {
                    "name": "Api key",
                    "key": "API_KEY",
                    "is_secure": True,
                    "value": "",
                },
                {
                    "name": "Api secret",
                    "key": "API_SECRET",
                    "is_secure": True,
                    "value": "",
                },
            ]
        }
    },
    {
        "name": "EMAIL",
        "tag": "EMAIL",
        "properties": [
            {
                "name": "Host",
                "key": "HOST",
                "value": "",
            },
            {
                "name": "Host User",
                "key": "HOST_USER",
                "value": "",
            },
            {
                "name": "Password",
                "key": "PASSWORD",
                "value": "",
                "is_secure": True,
            },
            {
                "name": "Port",
                "key": "PORT",
                "value": "",
            },
            {
                "name": "Default from email",
                "key": "DEFAULT_FROM_EMAIL",
                "value": "",
            },
            {
                "name": "USE TLS",
                "key": "USE_TLS",
                "value": "",
                "is_boolean": True
            },
        ]
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