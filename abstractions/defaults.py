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
            {
                "name": "Secret Key",
                "key": "SECRET_KEY",
                "value": "",
                "is_secure": True,
            },
            {
                "name": "Allowed Hosts",
                "key": "ALLOWED_HOSTS",
                "value": "",
                "help_text": "Specify your allowed hosts separated with a comma"
            },
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
                "value": "",
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