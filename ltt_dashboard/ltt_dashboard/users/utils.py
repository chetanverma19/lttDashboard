from django.core.mail import EmailMessage


class Util:

    @staticmethod
    def send_email(data):
        email_subject = data.get('email_subject')
        email_body = data.get('email_body')
        to_mail = data.get('to_mail')
        email = EmailMessage(subject=email_subject, body=email_body, to=[to_mail])
        email.send()

    @staticmethod
    def create_verify_message_for_user(user_data, verification_url):
        user_full_name = user_data.get('full_name')
        if not user_full_name:
            user_full_name = "New User"
        return f"Hi {user_full_name},\nPlease verify your account using the following link:\n{verification_url}"

    @staticmethod
    def get_successful_verification_message():
        return {
            "email": "Successfully Verifiied"
        }

    @staticmethod
    def get_timeout_verification_message(error_exception):
        return {
            "error": f"Verification Link Expired | {str(error_exception)}"
        }

    @staticmethod
    def get_invalid_token_error(error_exception):
        return {
            "error": f"Invalid Token | {str(error_exception)}"
        }
