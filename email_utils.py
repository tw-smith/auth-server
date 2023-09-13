from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from config import settings
from database.auth_models import TourTrackerUser
from jwt_utilities import JWTUserAccessToken


def send_verification_email(user: TourTrackerUser, service: str, base_url: str):
    token = JWTUserAccessToken(service, user)
    token = token.encode_jwt()
    verification_url = f"{base_url}?token={token}"
    if settings.production:
        sg = SendGridAPIClient(api_key=settings.sendgrid_api_key)
        message = Mail(
            from_email=settings.email_sender_address,
            to_emails=user.email,
            subject='Please verify your email address'
        )
        message.dynamic_template_data = {
            'username': user.username,
            'verification_url': verification_url
        }
        match service:
            case "tourtracker":
                message.template_id = settings.tourtracker_email_template_id
            case "arcade":
                message.template_id = settings.arcade_email_template_id
        try:
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e)

    if settings.development:
        print("EMAIL DEV MODE")
        with open("log.txt", mode="w") as email_file:
            content = f"notification for {user.email}: {user.username} URL is {verification_url}"
            email_file.write(content)
        return token
