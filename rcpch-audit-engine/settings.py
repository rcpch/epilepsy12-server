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

from dotenv import load_dotenv

# third party imports
from django.core.management.utils import get_random_secret_key

# Must be above importing logging settigns as we read environment variables there
load_dotenv('envs/.env')

# RCPCH imports
from .logging_settings import (
    LOGGING,
)  # no it is not an unused import, it pulls LOGGING into the settings file

logger = logging.getLogger(__name__)

load_dotenv("envs/.env")

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

# Mapbox
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

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
    "django.contrib.humanize",
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
    "epilepsy12.middleware.CurrentUserMiddleware",
    # 2fa
    "django_otp.middleware.OTPMiddleware",
]

# Django security middleware settings for HSTS support
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Session cookies
SESSION_COOKIE_SECURE = True  # enforces HTTPS
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True  # cannot access session cookie on client-side using JS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # session expires on browser close

ROOT_URLCONF = "rcpch-audit-engine.urls"

# AUTO LOGOUT SESSION EXPIRATION
AUTO_LOGOUT = {
    "IDLE_TIME": int(os.getenv("AUTO_LOGOUT_DELAY_SECONDS", 1800)),
    "REDIRECT_TO_LOGIN_IMMEDIATELY": True,
    "MESSAGE": "You have been automatically logged out as there was no activity for 30 minutes. Please login again to continue.",
}

# LOGIN_URL = "/registration/login/"
LOGIN_URL = "two_factor:login"  # change LOGIN_URL to the 2fa one
LOGIN_REDIRECT_URL = "two_factor:profile"
LOGOUT_REDIRECT_URL = "two_factor:login"

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
                "django_auto_logout.context_processors.auto_logout_client",  # auto logout
                "rcpch-audit-engine.build_info.get_build_info",
            ]
        },
    },
]

WSGI_APPLICATION = "rcpch-audit-engine.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

database_config = {
    "ENGINE": "django.contrib.gis.db.backends.postgis",
    "NAME": os.environ.get("E12_POSTGRES_DB_NAME"),
    "USER": os.environ.get("E12_POSTGRES_DB_USER"),
    "HOST": os.environ.get("E12_POSTGRES_DB_HOST"),
    "PORT": os.environ.get("E12_POSTGRES_DB_PORT"),
}

password_file = os.environ.get("E12_POSTGRES_DB_PASSWORD_FILE")

if password_file:
    database_config["OPTIONS"] = {"passfile": password_file}
else:
    database_config["PASSWORD"] = os.environ.get("E12_POSTGRES_DB_PASSWORD")

DATABASES = {"default": database_config}

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

# PASSWORD_RESET_TIMEOUT = os.environ.get(
#     "PASSWORD_RESET_TIMEOUT", 120
# )  # Default: 259200 (2 minutes, in seconds) - 2 minutes for testing

PASSWORD_RESET_TIMEOUT = os.environ.get(
    "PASSWORD_RESET_TIMEOUT", 259200
)  # Default: 259200 (3 days, in seconds)

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
