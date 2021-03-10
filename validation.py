import re

## Regex for validating the email as per the RFC2822
EMAIL_REGEX = "[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"

## Regex for Password based on the following conditions:
## 1. Password must be between 8 and 30 characters.
## 2. Password must contain at least one uppercase, or capital, letter (ex: A, B, etc.).
## 3. Password must contain at least one lowercase letter.
## 4. Password must contain at least one numeric digit (ex: 0, 1, 2, 3, etc.)
## 5. Password must contain at least one special character -for example, $, #, @, !,%,^,&,*,(,)

PASSWORD_REGEX = "^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[$#@!%^&*()])(?=\\S+$).{8, 20}$"

EMAIL_VALIDATION = "email"
PASSWORD_VALIDATION = "password"

VALIDATION_TYPES = [EMAIL_VALIDATION, PASSWORD_VALIDATION]

def validate(vtype=None, text=None):
    """Validates the 'text' argument based on the 'vtype' specified. 'vtype' corresponds to the type of 
        text i.e. 'email' or 'password'. Regex pattern for the different types is specified in this file.\n
        
        Keyword Arguments:
        vtype -- Type of validation required among 'email' or 'password'.\n
        text -- The text which is to be validated.\n
    """

    # Test the 'vtype' argument to be of type 'str'
    if not isinstance(vtype, str):
        print("Error: Invalid argument passed to 'vtype'. Required 'str', found {}".format(type(vtype)))
        return None

    # Test that the vtype argument is among the available Types
    if vtype not in VALIDATION_TYPES:
        print("Error: Invalid argument passed to 'vtype'. Can only be one of: {}".format(", ".join(VALIDATION_TYPES)))
        return None

    # Test the 'text' argument to be of type 'str'
    if not isinstance(text, str):
        print("Error: Invalid argument passed to 'text'. Required 'str', found {}".format(type(text)))
        return None

    ## Commented this so that the if password is empty, the function would not return here, but it will return False in the Validation test 
    # # Test that the vtype argument is among the available Types
    # if len(text) == 0:
    #     print("Error: Empty text passed to argument 'text'.")
    #     return None

    # Return True if the 'text' argument passes the test with the Regular Expression EMAIL_REGEX
    if vtype == EMAIL_VALIDATION:
        if re.search(EMAIL_REGEX, text):
            return True

        # Returns False if Email does not pass the Regex Test
        return False

    elif vtype == PASSWORD_VALIDATION:
    # Return true if the 'text' argument passes the test with the Regular Expression EMAIL_REGEX
        if re.search(PASSWORD_REGEX, text):
            return True

        # Returns False if Email does not pass the Regex Test
        return False
