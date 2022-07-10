from django.core.mail import EmailMessage


class Util:

    @staticmethod
    def send_email(data):
        email_subject = data.get('email_subject')
        email_body = data.get('email_body')
        to_mail = data.get('to_mail')
        if not isinstance(to_mail, list):
            to_mail = [to_mail]
        email = EmailMessage(subject=email_subject, body=email_body, to=to_mail)
        email.send()

    @staticmethod
    def create_verify_message_for_user(user_data, verification_url):
        user_full_name = user_data.get('full_name')
        if not user_full_name:
            user_full_name = "New User"
        return f"Hi {user_full_name},\nPlease verify your account using the following link:\n{verification_url}"

    @staticmethod
    def get_rejection_email(user_name, job_name):
        mail = {
            "email_subject": f"{job_name} Application Update",
            "email_body": f"Dear {user_name},\n\nWe regret to inform you but at this moment we have decided not to move"
                          f" forward with you application for the position of {job_name}. We appreciate for selecting "
                          f"LMG for your future endeavours.\n\nPlease feel free to try apply for more open positions "
                          f"available on our website at https://linusmediagroup.com/jobs\n\nThank You\nNOT Linus Media "
                          f"Group"
        }
        return mail

    @staticmethod
    def get_mass_rejection_email(job_name):
        mail = {
            "email_subject": f"{job_name} Application Update",
            "email_body": f"Dear Candidate,\n\nWe regret to inform you but at this moment we have decided not to move"
                          f" forward with you application for the position of {job_name}. We appreciate for selecting "
                          f"LMG for your future endeavours.\n\nPlease feel free to try apply for more open positions "
                          f"available on our website at https://linusmediagroup.com/jobs\n\nThank You\nNOT Linus Media "
                          f"Group"
        }
        return mail

    @staticmethod
    def get_application_submission_email(job_name):
        mail = {
            "email_subject": f"{job_name} Application Update",
            "email_body": f"Dear Candidate,\n\nWe have recieved your application for the position of {job_name}."
                          f"We appreciate for selecting LMG for your future endeavours.\n\nPlease feel free to try "
                          f"apply for more open positions  available on our website at "
                          f"https://linusmediagroup.com/jobs\n\nThank You\nNOT Linus Media Group"
        }
        return mail

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
