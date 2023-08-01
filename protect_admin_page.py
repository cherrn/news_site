import os


VALID_USERNAME = os.getenv('VALID_USERNAME')
VALID_PASSWORD = os.getenv('VALID_PASSWORD')


def is_authenticated(username, password):
    return username == VALID_USERNAME and password == VALID_PASSWORD
