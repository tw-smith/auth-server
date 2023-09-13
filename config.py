from pydantic import BaseSettings

# App configuration
class Settings(BaseSettings):
    app_name: str = "tw-smith Auth Server"
    secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    sendgrid_api_key: str
    email_sender_address: str
    development: bool
    production: bool
    tourtracker_email_template_id: str
    arcade_email_template_id: str

    class Config:
        env_file = ".env"


settings = Settings()