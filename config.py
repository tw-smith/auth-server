from starlette.datastructures import CommaSeparatedStrings, Secret
from starlette.config import Config

config = Config('.env')

class Settings():
    DEBUG = config('DEBUG', cast=bool, default=False)
    TESTING = config('TESTING', cast=bool, default=False)
    ALLOWED_ORIGINS = config('ALLOWED_ORIGINS', cast=CommaSeparatedStrings)

    if DEBUG or TESTING:
        BASE_URL = 'http://127.0.0.1:7000'
    else:
        BASE_URL = 'https://auth.tw-smith.me'

    # Keys etc
    SECRET_KEY = config('SECRET_KEY', cast=Secret)
    JWT_ALGORITHM = config('JWT_ALGORITHM', cast=str)
    ACCESS_TOKEN_EXPIRE_MINUTES = config('ACCESS_TOKEN_EXPIRE_MINUTES', cast=int, default=60)

    # API keys etc
    SENDGRID_API_KEY = config('SENDGRID_API_KEY', cast=Secret)

    # Email addresses
    EMAIL_SENDER_ADDRESS = config('EMAIL_SENDER_ADDRESS', cast=str)

    # Sendgrid Email Templates
    TOURTRACKER_VERIFICATION_EMAIL_TEMPLATE_ID = config('TOURTRACKER_VERIFICATION_EMAIL_TEMPLATE_ID', cast=str)
    TOURTRACKER_PASSWORD_RESET_EMAIL_TEMPLATE_ID = config('TOURTRACKER_PASSWORD_RESET_EMAIL_TEMPLATE_ID', cast=str)
    TOURTRACKER_PASSWORD_RESET_CONFIRMATION_EMAIL_TEMPLATE_ID = config('TOURTRACKER_PASSWORD_RESET_CONFIRMATION_EMAIL_TEMPLATE_ID', cast=str)
    ARCADE_VERIFICATION_EMAIL_TEMPLATE_ID = config('ARCADE_VERIFICATION_EMAIL_TEMPLATE_ID', cast=str)
    ARCADE_PASSWORD_RESET_EMAIL_TEMPLATE_ID = config('ARCADE_PASSWORD_RESET_EMAIL_TEMPLATE_ID', cast=str)
    ARCADE_PASSWORD_RESET_CONFIRMATION_EMAIL_TEMPLATE_ID = config('ARCADE_PASSWORD_RESET_CONFIRMATION_EMAIL_TEMPLATE_ID', cast=str)


settings = Settings()