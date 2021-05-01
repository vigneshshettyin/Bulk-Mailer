from json import load

from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from decouple import config

# Token is valid for 1 day
if len(config("email_verification_timeout")) != 0:
    MAX_TIME = int(config("email_verification_timeout"))
else:
    raise Exception(
        "Property 'email_verification_timeout' not set in 'import.json' file"
    )


# Salt
if len(config("email_verification_timeout")) != 0:
    VERIFICATION_SALT = config("email_verification_salt")
else:
    raise Exception("Property 'email_verification_salt' not set in 'import.json' file")

# Secret Key
if len(config("email_verification_timeout")) != 0:
    SECRET = config("email_verification_secret")
else:
    raise Exception(
        "Property 'email_verification_secret' not set in 'import.json' file"
    )


def validate_token(token=None):
    """Helps in confirming the Email Address with the help of the token, sent on the registered email address.\n
    Keyword Arguments:
    token -- Token passed in the user's email
    """
    try:
        res = URLSafeTimedSerializer(SECRET).loads(  # noqa
            token, salt=VERIFICATION_SALT, max_age=MAX_TIME
        )

    except SignatureExpired:
        return False

    # Token was successfully validated
    return True


def generate_token(email=None):
    """
    Returns a token for the purpose of email verification.\n
    Keyword Arguments
    email -- Email address for which the token is to be generated
    """
    if not isinstance(email, str) or len(email) == 0:
        print("Error: Invalid Email address passed")
        return None

    token = URLSafeTimedSerializer(SECRET).dumps(email, salt=VERIFICATION_SALT)

    # Return token for the email
    return token
