from penzi.common_settings import *
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l_g+tli6e)j=&(%$hjrmiokb^^80wh5ml((_bfg_@72g9wy)e5'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
