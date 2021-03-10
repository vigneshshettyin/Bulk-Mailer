from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# Token is valid for 1 day
MAX_TIME = 86400

# Salt 
VERIFICATION_SALT = "email-confirm"

# Secret Key
SECRET = "bulk-mailer"

def validate_token(token=None):
    """Helps in confirming the Email Address with the help of the token, sent on the registered email address.\n
        Keyword Arguments:
        token -- Token passed in the user's email
    """
    try:
        res = URLSafeTimedSerializer(SECRET).loads(token, salt=VERIFICATION_SALT, max_age=MAX_TIME)
    
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
    
    ## Return token for the email 
    return token