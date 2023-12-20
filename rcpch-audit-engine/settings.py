"""
Django settings for rcpch-audit-engine project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""


# standard imports
import datetime
import logging
import os
from pathlib import Path

# third party imports
from celery.schedules import crontab
from django.core.management.utils import get_random_secret_key

# RCPCH imports

logger = logging.getLogger(__name__)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"
if DEBUG is True:
    CAPTCHA_TEST_MODE = True  # if in debug mode, can just type 'PASSED' and captcha validates. Default value is False

# GENERAL CAPTCHA SETTINGS
CAPTCHA_IMAGE_SIZE = (200, 50)
CAPTCHA_FONT_SIZE = 40

# Need to handle missing ENV var
# Need to handle duplicates
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") + [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
]
CSRF_TRUSTED_ORIGINS = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",") + [
    "https://127.0.0.1",
    "https://localhost",
    "https://0.0.0.0",
]

# Enables Django to use the X-Forwarded-Host header in preference to the Host header.
# Fixes CSRF errors when using Caddy to forward requests to Django.
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# This is the token required for getting deprivation quintiles from the RCPCH Census Platform
RCPCH_CENSUS_PLATFORM_URL = os.getenv("RCPCH_CENSUS_PLATFORM_URL")
RCPCH_CENSUS_PLATFORM_TOKEN = os.getenv("RCPCH_CENSUS_PLATFORM_TOKEN")

# Postcode API
POSTCODE_API_BASE_URL = os.getenv("POSTCODE_API_BASE_URL")

NHS_ODS_API_URL = os.getenv("NHS_ODS_API_URL")
NHS_ODS_API_KEY = os.getenv("NHS_ODS_API_KEY")

# SNOMED Terminology server
RCPCH_HERMES_SERVER_URL = os.getenv("RCPCH_HERMES_SERVER_URL")

# Application definition

INSTALLED_APPS = [
    "semantic_admin",
    "django.contrib.gis",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admindocs",
    "rest_framework",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    # third party
    "widget_tweaks",
    "django_htmx",
    "rest_framework.authtoken",
    "simple_history",
    "django_filters",
    # 2fa
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_email",
    "two_factor.plugins.email",
    "two_factor",
    "two_factor.plugins.phonenumber",  # we don't use phones currently but required for app to work
    # captcha
    "captcha",
    # application
    "epilepsy12",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "django_auto_logout.middleware.auto_logout",
    # 2fa
    "django_otp.middleware.OTPMiddleware",
]

# Django security middleware settings for HSTS support
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
# SESSION_COOKIE_SECURE = True

ROOT_URLCONF = "rcpch-audit-engine.urls"

# AUTO LOGOUT SESSION EXPIRATION
AUTO_LOGOUT = {
    "IDLE_TIME": datetime.timedelta(minutes=30),
    "REDIRECT_TO_LOGIN_IMMEDIATELY": True,
    "MESSAGE": "You have been automatically logged out as there was no activity for 30 minutes. Please login again to continue.",
}

# LOGIN_URL = "/registration/login/"
LOGIN_URL = "two_factor:login"  # change LOGIN_URL to the 2fa one
LOGIN_REDIRECT_URL = "two_factor:profile"
LOGOUT_REDIRECT_URL = "/"

# REDIS / Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/London"

# CELERY_BEAT_SCHEDULE = {
#     "run-daily-at-six-am": {
#         "task": "epilepsy12.tasks.hello",
#         "schedule": crontab(hour="6", minute=0),
#         "options": {
#             "expires": 15.0,
#         },
#     },
#     "run-ever-10-seconds": {
#         "task": "epilepsy12.tasks.hello",
#         "schedule": 10,
#         "options": {
#             "expires": 15.0,
#         },
#     },

# }

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_auto_logout.context_processors.auto_logout_client",
                "rcpch-audit-engine.git_context_processor.get_active_branch_and_commit",
            ]
        },
    },
]

WSGI_APPLICATION = "rcpch-audit-engine.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.environ.get("E12_POSTGRES_DB_NAME"),
        "USER": os.environ.get("E12_POSTGRES_DB_USER"),
        "PASSWORD": os.environ.get("E12_POSTGRES_DB_PASSWORD"),
        "HOST": os.environ.get("E12_POSTGRES_DB_HOST"),
        "PORT": os.environ.get("E12_POSTGRES_DB_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "epilepsy12.validators.CapitalAndSymbolValidator",
        "OPTIONS": {
            "symbols": "!@£$%^&*()_-+=|~",
            "number_of_symbols": 1,
            "number_of_capitals": 1,
        },
    },
    {
        "NAME": "epilepsy12.validators.NumberValidator",  # must have one number
    },
]

AUTH_USER_MODEL = "epilepsy12.Epilepsy12User"

# Two Factor Authentication / One Time Password Settings (2FA / one-time login codes)
OTP_EMAIL_SUBJECT = "Your Epilepsy12 one-time login code"
OTP_EMAIL_BODY_TEMPLATE_PATH = "../templates/two_factor/email_token.txt"
OTP_EMAIL_BODY_HTML_TEMPLATE_PATH = "../templates/two_factor/email_token.html"
OTP_EMAIL_TOKEN_VALIDITY = 60 * 5  # default N(seconds) email token valid for

# EMAIL SETTINGS (SMTP)
DEFAULT_FROM_EMAIL = os.environ.get("EMAIL_DEFAULT_FROM_EMAIL")
SMTP_EMAIL_ENABLED = os.getenv("SMTP_EMAIL_ENABLED", "False") == "True"
logger.info("SMTP_EMAIL_ENABLED: %s", SMTP_EMAIL_ENABLED)
if SMTP_EMAIL_ENABLED is True:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ.get("EMAIL_HOST_SERVER")
    EMAIL_PORT = os.environ.get("EMAIL_HOST_PORT")
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
    EMAIL_USE_TLS = True
    EMAIL_TIMEOUT = 10
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
logger.info("EMAIL_BACKEND: %s", EMAIL_BACKEND)

PASSWORD_RESET_TIMEOUT = 259200  # Default: 259200 (3 days, in seconds)

SITE_CONTACT_EMAIL = os.environ.get("SITE_CONTACT_EMAIL")


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/London"

USE_I18N = True

# The USE_L10N setting is deprecated. Starting with Django 5.0, localized formatting of data will always be enabled. For example Django will display numbers and dates using the format of the current locale.
# USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = (str(BASE_DIR.joinpath("static")),)
STATIC_ROOT = str(BASE_DIR.joinpath("staticfiles"))
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
WHITENOISE_ROOT = os.path.join(BASE_DIR, "static/root")

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",  # this is default
)

# rest framework settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
}

# LOGGING
CONSOLE_LOG_LEVEL = os.getenv("CONSOLE_LOG_LEVEL", "INFO") # For e12 specific logs
CONSOLE_DJANGO_LOG_LEVEL = os.getenv("CONSOLE_DJANGO_LOG_LEVEL", "INFO") # For django logs
FILE_LOG_LEVEL = os.getenv("FILE_LOG_LEVEL", "INFO")


# Define the default django logger settings
django_loggers = {
    logger_name: {
        "handlers": ["django_console"],
        "level": CONSOLE_DJANGO_LOG_LEVEL,
        "propagate": False,
        "formatter": "simple_django",
    }
    for logger_name in (
        "django.request",
        "django.utils",  # The django.utils logger logs events from Django and other miscellaneous log events e.g. autoreload
        "django.security",
        "django.db.backends",  # The django.db.backends logger logs SQL queries. Set the level to DEBUG or higher to log SQL queries.
        "django.template",
        "django.server",  # The django.server logger logs events from the runserver command.
    )
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {},
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[{server_time}] {message}",
            "style": "{",
        },
        # Same as verbose, but no color formatting
        "file": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "verbose": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(bold_white)s%(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
            "log_colors": {
                "DEBUG": "bold_black",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "simple": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s [%(name)s:%(lineno)s] %(bold_white)s%(message)s",
            "log_colors": {
                "DEBUG": "bold_black",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        # Don't need line numbers for default django loggers
        "simple_django": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s [%(name)s] %(bold_white)s%(message)s",
            "log_colors": {
                "DEBUG": "bold_black",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
    },
    "handlers": {
        "epilepsy12_console": {
            "level": CONSOLE_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "filters": [],
        },
        "django_console": {
            "level": CONSOLE_DJANGO_LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple_django",
            "filters": [],
        },
        # Optional separate file logger if required
        "general_file": {
            "level": FILE_LOG_LEVEL,
            "class": "logging.FileHandler",
            "filename": "logs/general.log",
            "formatter": "file",
        },
        # e12 file logger, each file is 15MB max, with 10 historic versions when filled, post-fixed with .1, .2, ..., .10 
        "epilepsy12_logs": {
            "level": FILE_LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/epilepsy12.log",
            "maxBytes": 15728640,  # 1024 * 1024 * 15B = 15MB
            "backupCount": 10,
            "formatter": "file",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django_console", "epilepsy12_logs"],
            "propagate": True,
        },
        **django_loggers,  # this injects the default django logger settings defined above
        "epilepsy12": {
            "handlers": ["epilepsy12_console", "epilepsy12_logs"],
            "propagate": False,
        },
        "two_factor": {
            "handlers": ["epilepsy12_console", "epilepsy12_logs"],
        },
    },
}