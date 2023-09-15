from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from config import settings
from database.auth_models import TourTrackerUser, ArcadeUser, BaseUser
from jwt_utilities import encode_jwt
from datetime import timedelta



class AuthEmail:
    def __init__(self, user: BaseUser, service: str, base_url: str = ''):
        self.user = user
        self.service = service
        self.base_url = base_url
        self.url_path = ''
        self.payload = {
            "sub": self.user.public_id
        }
        self.token_url = self.generate_token_url()
        self.email_subject = ''
        self.sendgrid_template_id = ''

    def generate_token_url(self):
        token = encode_jwt(self.payload, self.service, expires_delta=timedelta(minutes=15))
        return f"{self.base_url}{self.url_path}?token={token}"

    def send_email(self):
        if settings.production:
            sg = SendGridAPIClient(api_key=settings.sendgrid_api_key)
            message = Mail(
                from_email=settings.email_sender_address,
                to_emails=self.user.email,
                subject=self.email_subject
            )
            message.dynamic_template_data = {
                'username': self.user.username,
                'token_url': self.token_url
            }
            message.template_id = self.sendgrid_template_id
            try:
                response = sg.send(message)
            except Exception as e:
                print(e)
        if settings.development:
            print("EMAIL DEV MODE")
            print(self.token_url)
            return self.email_subject, self.token_url


class PasswordResetEmail(AuthEmail):
    def __init__(self, user: BaseUser, service: str, base_url: str = ''):
        super().__init__(user, service, base_url)
        self.email_subject = "Password Reset Email"
        self.url_path = '/resetpassword'
        self.token_url = self.generate_token_url()
        match self.service:
            case "tourtracker":
                self.sendgrid_template_id = settings.tourtracker_password_reset_email_template_id
            case "arcade":
                self.sendgrid_template_id = settings.arcade_password_reset_email_template_id

    # Override parent token generation to create one time use token using password hash and user creation time
    def generate_token_url(self):
        secret_key = f"{self.user.password_hash}_{self.user.created_at}"
        token = encode_jwt(self.payload, self.service, expires_delta=timedelta(minutes=15), secret_key=secret_key)
        return f"{self.base_url}{self.url_path}?username={self.user.username}&service={self.service}&token={token}"


class PasswordResetConfirmationEmail(AuthEmail):
    def __init__(self, user: BaseUser, service: str, base_url: str = ''):
        super().__init__(user, service, base_url)
        self.email_subject = 'Successful Password Reset'
        match self.service:
            case "tourtracker":
                self.sendgrid_template_id = settings.tourtracker_password_reset_confirmation_email_template_id
            case "arcade":
                self.sendgrid_template_id = settings.arcade_password_reset_confirmation_email_template_id



class VerificationEmail(AuthEmail):
    def __init__(self, user: BaseUser, service: str, base_url: str = ''):
        super().__init__(user, service, base_url)
        self.email_subject = "Please verify your email address"
        self.url_path = '/verify'
        match self.service:
            case "tourtracker":
                self.sendgrid_template_id = settings.tourtracker_verification_email_template_id
            case "arcade":
                self.sendgrid_template_id = settings.arcade_verification_email_template_id
