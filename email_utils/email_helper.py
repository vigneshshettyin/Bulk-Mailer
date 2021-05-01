import json

from decouple import config

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def mail_handler(recepient_email=None, subject=None, content=None):
    """
    Uses Sendgrid Api to send a mail to the receipients.\n
    Keyword Arguments\n
    recepient_email -- The email address of the receipient.\n
    subject -- Subject of the email address.\n
    content -- Body of the email address.\n

    Returns True if there is no error, or will return the error message.
    """

    message = Mail(
        from_email=("rohit.is.here99@gmail.com", "Bulk Mailer Register"),
        to_emails=recepient_email,
        subject=subject,
        html_content=content,
    )

    try:
        # using the sendgrid api, send the email to the user's email
        sg = SendGridAPIClient(config("sendgridapi"))
        response = sg.send(message)  # noqa
        # flash('Email Sent Successfully!', success)
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
    except Exception as e:  # noqa
        # if an error occurs flash a msg
        return False

    # Returns true if no error occured
    return True
