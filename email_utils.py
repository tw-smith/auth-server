from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from urllib.parse import urlencode
import os
from config import settings
from database.auth_models import TourTrackerUser, ArcadeUser, BaseUser
from jwt_utilities import encode_jwt
from datetime import timedelta



class AuthEmail:
    def __init__(self, user: BaseUser, service: str, base_url: str = '', redirect_url: str = ''):
        self.user = user
        self.service = service
        self.base_url = base_url
        self.redirect_url = redirect_url
        self.url_path = ''
        self.payload = {
            "sub": self.user.public_id
        }
        self.token_url = self.generate_token_url()
        self.email_subject = ''
        self.sendgrid_template_id = ''

    def generate_token_url(self):
        token = encode_jwt(self.payload, self.service, expires_delta=timedelta(minutes=15))
        params = {
            'token': token,
            'redirect_url': self.redirect_url
        }
        return f"{self.base_url}{self.url_path}?{urlencode(params)}"

    def send_email(self):
        if settings.DEBUG or settings.TESTING:
            print("EMAIL DEV MODE")
            print(self.token_url)
            return self.email_subject, self.token_url
        sg = SendGridAPIClient(api_key=str(settings.SENDGRID_API_KEY))
        message = Mail(
            from_email=settings.EMAIL_SENDER_ADDRESS,
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



class PasswordResetEmail(AuthEmail):
    def __init__(self, user: BaseUser, service: str, base_url: str = settings.BASE_URL, redirect_url=''):
        super().__init__(user, service, base_url, redirect_url)
        self.email_subject = "Password Reset Email"
        self.url_path = '/resetpassword'
        self.token_url = self.generate_token_url()
        match self.service:
            case "tourtracker":
                self.sendgrid_template_id = settings.TOURTRACKER_PASSWORD_RESET_EMAIL_TEMPLATE_ID
            case "arcade":
                self.sendgrid_template_id = settings.ARCADE_PASSWORD_RESET_EMAIL_TEMPLATE_ID

    # Override parent token generation to create one time use token using password hash and user creation time
    def generate_token_url(self):
        secret_key = f"{self.user.password_hash}_{self.user.created_at}"
        token = encode_jwt(self.payload, self.service, expires_delta=timedelta(minutes=15), secret_key=secret_key)
        params = {
            'username': self.user.username,
            'service': self.service,
            'token': token,
            'redirect_url': self.redirect_url
        }
        return f"{self.base_url}{self.url_path}?{urlencode(params)}"


class PasswordResetConfirmationEmail(AuthEmail):
    def __init__(self, user: BaseUser, service: str, base_url: str = '', redirect_url=''):
        super().__init__(user, service, base_url, redirect_url)
        self.email_subject = 'Successful Password Reset'
        match self.service:
            case "tourtracker":
                self.sendgrid_template_id = settings.TOURTRACKER_PASSWORD_RESET_CONFIRMATION_EMAIL_TEMPLATE_ID
            case "arcade":
                self.sendgrid_template_id = settings.ARCADE_PASSWORD_RESET_CONFIRMATION_EMAIL_TEMPLATE_ID



class VerificationEmail(AuthEmail):
    def __init__(self, user: BaseUser, service: str, base_url: str = '', redirect_url=''):
        super().__init__(user, service, base_url, redirect_url)
        self.email_subject = "Please verify your email address"
        self.url_path = '/verify'
        match self.service:
            case "tourtracker":
                self.sendgrid_template_id = settings.TOURTRACKER_VERIFICATION_EMAIL_TEMPLATE_ID
            case "arcade":
                self.sendgrid_template_id = settings.ARCADE_VERIFICATION_EMAIL_TEMPLATE_ID
