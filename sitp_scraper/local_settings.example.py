DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': '',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

MAPBOX_ACCESS_TOKEN = ''

TELEGRAM_TOKEN = ''

FACEBOOK_PAGE_ACCESS_TOKEN = ''
FACEBOOK_VERIFY_TOKEN = ''

import raven
import os

RAVEN_CONFIG = {
    'dsn': '',
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}
