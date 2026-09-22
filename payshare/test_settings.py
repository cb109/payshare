from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# The default PBKDF2 hasher is deliberately slow; tests don't need that.
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
