from flask import request, make_response
from functools import wraps
import mysql.connector
import re
import os
import uuid

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

UNSPLASH_ACCESS_KEY = 'YOUR_KEY_HERE'   
ADMIN_ROLE_PK = "16fd2706-8baf-433b-82eb-8c7fada847da"
CUSTOMER_ROLE_PK = "c56a4180-65aa-42ec-a945-5fd21dec0538"
PARTNER_ROLE_PK = "f47ac10b-58cc-4372-a567-0e02b2c3d479"
RESTAURANT_ROLE_PK = "9f8c8d22-5a67-4b6c-89d7-58f8b8cb4e15"


# form to get data from input fields
# args to get data from the url
# values to get data from the url and from the form

class CustomException(Exception):
    def __init__(self, message, code):
        super().__init__(message)  # Initialize the base class with the message
        self.message = message  # Store additional information (e.g., error code)
        self.code = code  # Store additional information (e.g., error code)

def raise_custom_exception(error, status_code):
    raise CustomException(error, status_code)


##############################
def db():
    db = mysql.connector.connect(
        host="mysql",      # Replace with your MySQL server's address or docker service name "mysql"
        user="root",  # Replace with your MySQL username
        password="password",  # Replace with your MySQL password
        database="company"   # Replace with your MySQL database name
    )
    cursor = db.cursor(dictionary=True)
    return db, cursor


##############################
def no_cache(view):
    @wraps(view)
    def no_cache_view(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    return no_cache_view


##############################

def allow_origin(origin="*"):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Call the wrapped function
            response = make_response(f(*args, **kwargs))
            # Add Access-Control-Allow-Origin header to the response
            response.headers["Access-Control-Allow-Origin"] = origin
            # Optionally allow other methods and headers for full CORS support
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        return decorated_function
    return decorator


NAME_MIN = 2
NAME_MAX = 50
NAME_REGEX = f"^.{{{NAME_MIN},{NAME_MAX}}}$"
PASSWORD_MIN = 8
PASSWORD_MAX = 50
PASSWORD_REGEX = f"^.{{{PASSWORD_MIN},{PASSWORD_MAX}}}$"

EMAIL_REGEX = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
UUID4_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

USER_ROLES = ["customer", "partner"]
UPLOAD_ITEM_FOLDER = './images'
ALLOWED_ITEM_FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


##############################
def validate_user_name():
    error = f"Name must be {NAME_MIN} to {NAME_MAX} characters."
    user_name = request.form.get("user_name", "").strip()
    if not re.match(NAME_REGEX, user_name): raise_custom_exception(error, 400)
    return user_name


##############################
def validate_user_last_name():
    error = f"Lastname must be {NAME_MIN} to {NAME_MAX} characters."
    user_last_name = request.form.get("user_last_name", "").strip() # None
    if not re.match(NAME_REGEX, user_last_name): raise_custom_exception(error, 400)
    return user_last_name


##############################
def validate_user_email():
    error = "email invalid"
    user_email = request.form.get("user_email", "").strip()
    if not re.match(EMAIL_REGEX, user_email): raise_custom_exception(error, 400)
    return user_email


##############################
def validate_user_password():
    error = f"password {PASSWORD_MIN} to {PASSWORD_MAX} characters"
    user_password = request.form.get("user_password", "").strip()
    if not re.match(PASSWORD_REGEX, user_password): raise_custom_exception(error, 400)
    return user_password


##############################
def validate_uuid4(uuid4 = ""):
    error = f"invalid uuid4"
    if not uuid4:
        uuid4 = request.values.get("uuid4", "").strip()
    if not re.match(UUID4_REGEX, uuid4): raise_custom_exception(error, 400)
    return uuid4


##############################
def validate_user_role():
    user_role = request.form.get("user_role", "")
    if not user_role: 
        raise_custom_exception("role is required", 400)
    if user_role not in USER_ROLES: 
        raise_custom_exception("invalid role", 400)
    return user_role


##############################
def validate_restaurant_name():
    error = f"name {NAME_MIN} to {NAME_MAX} characters"
    restaurant_name = request.form.get("restaurant_name", "")
    if not re.match(NAME_REGEX, restaurant_name): raise_custom_exception(error, 400)
    return restaurant_name


##############################
def validate_restaurant_email():
    error = "email invalid"
    restaurant_email = request.form.get("restaurant_email", "").strip()
    if not re.match(EMAIL_REGEX, restaurant_email): raise_custom_exception(error, 400)
    return restaurant_email


##############################
def validate_restaurant_password():
    error = f"password {PASSWORD_MIN} to {PASSWORD_MAX} characters"
    restaurant_password = request.form.get("restaurant_password", "").strip()
    if not re.match(PASSWORD_REGEX, restaurant_password): raise_custom_exception(error, 400)
    return restaurant_password


##############################

def validate_item_image():
    if 'item_file' not in request.files: raise_custom_exception("item_file missing", 400)
    file = request.files.get("item_file", "")
    if file.filename == "": raise_custom_exception("item_file name invalid", 400)

    if file:
        ic(file.filename)
        file_extension = os.path.splitext(file.filename)[1][1:]
        ic(file_extension)
        if file_extension not in ALLOWED_ITEM_FILE_EXTENSIONS: raise_custom_exception("item_file invalid extension", 400)
        filename = str(uuid.uuid4()) + file_extension
        return file, filename 

##############################
def send_verify_email(to_email, user_verification_key):
    try:
        # Create a gmail fullflaskdemomail
        # Enable (turn on) 2 step verification/factor in the google account manager
        # Visit: https://myaccount.google.com/apppasswords


        # Email and password of the sender's Gmail account
        sender_email = "sofiefuglsanghyllen@gmail.com"
        password = "jsdfsqosuxtlakab"  # If 2FA is on, use an App Password instead

        # Receiver email address
        receiver_email = to_email
        
        # Create the email message
        message = MIMEMultipart()
        message["From"] = "My company name"
        message["To"] = receiver_email
        message["Subject"] = "Please verify your account"

        # Body of the email
        body = f"""To verify your account, please <a href="http://127.0.0.1/verify/{user_verification_key}">click here</a>"""
        message.attach(MIMEText(body, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")

        return "email sent"

    except Exception as ex:
        raise_custom_exception("cannot send email", 500)
    finally:
        pass




