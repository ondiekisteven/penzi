from penzi.common_settings import *

SECRET_KEY = 'l_g+tli6e)j=&(%$hjrmiokb^^80wh5ml((_bfg_@72g9wy)e5'

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': 5432,
    }
}

