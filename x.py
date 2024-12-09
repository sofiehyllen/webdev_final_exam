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

DESCRIPTION_MIN = 2
DESCRIPTION_MAX = 255
DESCRIPTION_REGEX = f"^.{{{DESCRIPTION_MIN},{DESCRIPTION_MAX}}}$"

PASSWORD_MIN = 8
PASSWORD_MAX = 50
PASSWORD_REGEX = f"^.{{{PASSWORD_MIN},{PASSWORD_MAX}}}$"

ADDRESS_MIN = 2
ADDRESS_MAX = 255
ADDRESS_REGEX = f"^.{{{ADDRESS_MIN},{ADDRESS_MAX}}}$"

POSTALCODE_REGEX = "^\d{4}$"

PRICE_MIN = 0
PRICE_MAX = 9999.99
PRICE_REGEX = "^\d{1,4}(\.\d{1,2})?$"

EMAIL_REGEX = "^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
UUID4_REGEX = "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"

USER_ROLES = ["customer", "partner"]

UPLOAD_ITEM_FOLDER = 'static/item_images'
UPLOAD_RESTAURANT_FOLDER = 'static/restaurant_images'
ALLOWED_FILE_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
ALLOWED_FILE_REGEX = "^.*\.(png|jpg|jpeg|gif)$"

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
def validate_account_name(form_field):
    error = f"name {NAME_MIN} to {NAME_MAX} characters."
    account_name = request.form.get(form_field, "").strip()
    if not re.match(NAME_REGEX, account_name): raise_custom_exception(error, 400)
    return account_name


##############################
def validate_account_email(form_field):
    error = "Email invalid"
    account_email = request.form.get(form_field, "").strip()
    if not re.match(EMAIL_REGEX, account_email): raise_custom_exception(error, 400)
    return account_email


##############################
def validate_account_password(form_field):
    error = f"password {PASSWORD_MIN} to {PASSWORD_MAX} characters"
    account_password = request.form.get(form_field, "").strip()
    if not re.match(PASSWORD_REGEX, account_password): raise_custom_exception(error, 400)
    return account_password


##############################
def validate_account_address(form_field):
    error = f"address {ADDRESS_MIN} to {ADDRESS_MAX} characters"
    account_address = request.form.get(form_field, "").strip()
    if not re.match(ADDRESS_REGEX, account_address): raise_custom_exception(error, 400)
    return account_address



##############################
def validate_account_address(form_field):
    error = f"address {ADDRESS_MIN} to {ADDRESS_MAX} characters"
    account_address = request.form.get(form_field, "").strip()
    if not re.match(ADDRESS_REGEX, account_address): raise_custom_exception(error, 400)
    return account_address



##############################
def validate_account_postalcode(form_field):
    error = f"postalcode incorrect"
    account_postalcode = request.form.get(form_field, "").strip()
    if not re.match(POSTALCODE_REGEX, account_postalcode): raise_custom_exception(error, 400)
    return account_postalcode



##############################
def validate_item_description():
    error = f"description {NAME_MIN} to {DESCRIPTION_MAX} characters"
    item_description = request.form.get("item_description", "").strip()
    if not re.match(DESCRIPTION_REGEX, item_description): raise_custom_exception(error, 400)
    return item_description


##############################
def validate_item_price():
    error = f"price {PRICE_MIN} to {PRICE_MAX}"
    item_price = request.form.get("item_price", "").strip()
    if not re.match(PRICE_REGEX, item_price): raise_custom_exception(error, 400)
    return item_price



##############################
def validate_search_field():
    error = f"searchfield {NAME_MIN} to {NAME_MAX} characters."
    search_text = request.args.get("search_field", "").strip()
    if not re.match(NAME_REGEX, search_text): raise_custom_exception(error, 400)
    return search_text



##############################
def validate_item_image(form_field):
    if form_field not in request.files: 
        raise_custom_exception("item_file missing", 400)

    files = request.files.getlist(form_field)
    if not files:
        raise_custom_exception("item_file name invalid", 400)

    valid_files = []

    for file in files:
        if file.filename == "": 
            raise_custom_exception("File missing", 400)

        # Validate file extension
        file_extension = os.path.splitext(file.filename)[1][1:]
        if file_extension not in ALLOWED_FILE_EXTENSIONS:
            raise_custom_exception("File invalid type", 400)

        # Generate a unique filename
        filename = f"{uuid.uuid4()}.{file_extension}"
        valid_files.append((file, filename))  # Store the valid file and its new name

    if not valid_files:
        raise_custom_exception("No valid files uploaded", 400)

    return valid_files 

    # if file:
    #     ic(file.filename)
    #     file_extension = os.path.splitext(file.filename)[1][1:]
    #     ic(file_extension)
    #     if file_extension not in ALLOWED_FILE_EXTENSIONS: raise_custom_exception("item_file invalid extension", 400)
    #     filename = f"{uuid.uuid4()}.{file_extension}"
    #     return file, filename 



##############################
def send_email(to_email, subject, body):
    try:
        # Email and password of the sender's Gmail account
        sender_email = "exampythonmail@gmail.com"
        password = "qtgoaneaffxkqcjp"  # Use an App Password if 2FA is on

        # Create the email message
        message = MIMEMultipart()
        message["From"] = "My company name"
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Upgrade connection to secure
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, message.as_string())

        print(f"{subject} email sent successfully!")
        return f"{subject} email sent"
    
    except Exception as ex:
        raise_custom_exception(f"cannot send {subject.lower()} email", 500)
    finally:
        pass



##############################
def send_verify_email(to_email, account_verification_key):
    body = f"""To verify your account, please <a href="http://127.0.0.1/verify/{account_verification_key}">click here</a>"""
    return send_email(to_email, "Verify your account", body)



##############################
def send_reset_password_email(to_email, account_password_reset_key):
    body = f"""
    <p>Hello,</p>
    <p>We received a request to reset your password. If you made this request, please click the link below to reset your password:</p>
    <p><a href="http://127.0.0.1/reset-password/{account_password_reset_key}">Reset Your Password</a></p>
    <p>If you did not request a password reset, you can safely ignore this email. Your password will remain the same.</p>
    <p>Thank you,<br>My company name</p>
    """
    return send_email(to_email, "Reset Your Password", body)



##############################
def send_block_email(to_email):
    body = f"""
    <p>Hello,</p>
    <p>We contact you to inform you that your account has been blocked. If you have any questions, feel free to contact us.</p>
    <p>Sincerely,<br>My company name</p>
    """
    return send_email(to_email, "Your account has been blocked", body)



##############################
def send_item_block_email(to_email):
    body = f"""
    <p>Hello,</p>
    <p>We contact you to inform you that one of your menu items has been blocked. If you have any questions, feel free to contact us.</p>
    <p>Sincerely,<br>My company name</p>
    """
    return send_email(to_email, "Your menu item has been blocked", body)



##############################
def send_delete_email(to_email):
    body = f"""
    <p>Hello,</p>
    <p>We contact you to inform you that your account has been deleted. If you have any questions, feel free to contact us.</p>
    <p>Sincerely,<br>My company name</p>
    """
    return send_email(to_email, "Your account has been deleted", body)



##############################
def send_item_delete_email(to_email):
    body = f"""
    <p>Hello,</p>
    <p>We contact you to inform you that one of your menu items has been deleted. If you have any questions, feel free to contact us.</p>
    <p>Sincerely,<br>My company name</p>
    """
    return send_email(to_email, "Your menu item has been deleted", body)



##############################
def send_order_confirmation_email(to_email, order_details, total_price):
    body = f"""
    <p>Hello,</p>
    <p>Thank you for your order! Below are the details of your purchase:</p>
    {order_details}
    <p><strong>Total Price: DKK {total_price}</strong></p>
    <p>We will process your order shortly. Thank you for shopping with us!</p>
    <p>Sincerely,<br>My company name</p>
    """
    return send_email(to_email, "Order Confirmation", body)

def format_order_details(items):
    order_details = "<h3>Your Order Details:</h3><ul>"
    
    for item in items:
        order_details += f"""
            <li>
                <p><strong>{item['item_title']}</strong></p>
                <p>Quantity: {item['quantity']}</p>
                <p>Price: DKK {item['item_price']}</p>
            </li>
        """
    
    order_details += "</ul>"
    return order_details