"""
Django settings for arbitration project.

Generated by 'django-admin startproject' using Django 3.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import os
import sys
from pathlib import Path

import dj_database_url
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "True") == "True"

ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost"
).split(",")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
    'rest_framework',
    'bootstrap5',
    'django_select2',
    'widget_tweaks',
    'crypto_exchanges.apps.CryptoExchangesConfig',
    'banks.apps.BanksConfig',
    'core.apps.CoreConfig',
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

ROOT_URLCONF = 'arbitration.urls'

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR],
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
]

WSGI_APPLICATION = 'arbitration.wsgi.application'

MULTITHREADING_MODE = os.getenv("MULTITHREADING_MODE", "True") == "True"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "True") == "True"

if DEVELOPMENT_MODE is True:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
elif len(sys.argv) > 0 and sys.argv[1] != 'collectstatic':
    if os.getenv("DATABASE_URL", None) is None:
        raise Exception("DATABASE_URL environment variable not defined")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USER'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST'),
            'PORT': os.getenv('DATABASE_PORT'),
            },
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
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
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'ru-ru'  # 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery settings
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"


CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
    },
    # … default cache config and others
    "select2": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Tell select2 which cache configuration to use:
SELECT2_CACHE_BACKEND = "select2"
