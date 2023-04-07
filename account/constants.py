"""
It contains all constant values
"""
REGEX = {
    "first_name": r'^[a-zA-Z]+$',
    "last_name": r'^[a-zA-Z]+$',
    "USERNAME": r'^(?=.*[!@#$%^&*()_+|~=`{}\[\]:";\'<>?,.\/])(?=.*[a-zA-Z0-9])'
                r'[a-zA-Z0-9!@#$%^&*()_+|~=`{}\[\]:";\'<>?,.\/]{8,}$',
    "contact": r'^\d+$',
    "PASSWORD": r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+=-])[0-9a-zA-Z!@#$%^&*()_+=-]{8,16}$',
}

MAX_LENGTH = {
    'first_name': 30,
    'last_name': 30,
    'username': 16,
    'password': 16,
    'contact': 10
}

MIN_LENGTH = {
    'first_name': 3,
    'last_name': 3,
    'username': 8,
    'password': 8,
    'contact': 10,
}

DIRECTORY_PATH = 'media/'
