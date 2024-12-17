import uuid
import time
from werkzeug.security import generate_password_hash
from icecream import ic
import x
from faker import Faker
import random

fake = Faker()

# Configure the output for icecream
ic.configureOutput(prefix=f'***** | ', includeContext=True)

db, cursor = x.db()
# Create a function to insert users into the database
def insert_user(user):
    try:
        q = """
            INSERT INTO users
            (user_pk, user_name, user_last_name, user_street, user_postalcode, user_city, 
            user_email, user_password, user_created_at, user_deleted_at, user_blocked_at, 
            user_updated_at, user_verified_at, user_verification_key, user_reset_password_key) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = tuple(user.values())
        cursor.execute(q, values)
    except Exception as ex:
        print(f"Error inserting user: {ex}")
        raise ex  # Re-raise the exception to be caught in the outer block

# Open database connection and get cursor


try:
    cursor.execute("DELETE FROM users")
    ##############################
    # Create admin user
    user_pk = str(uuid.uuid4())
    admin_user = {
        "user_pk": user_pk,
        "user_name": "John",
        "user_last_name": "Admin",
        "user_street": "Nørrebrogade 2",
        "user_postalcode": 2200,
        "user_city": "København",
        "user_email": "admin@company.com",
        "user_password": generate_password_hash("password"),
        "user_created_at": int(time.time()),
        "user_deleted_at": 0,
        "user_blocked_at": 0,
        "user_updated_at": 0,
        "user_verified_at": int(time.time()),
        "user_verification_key": str(uuid.uuid4()),
        "user_reset_password_key": 0
    }
    insert_user(admin_user)

    # Insert admin role
    cursor.execute("""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) 
        VALUES (%s, %s)
    """, (user_pk, x.ADMIN_ROLE_PK))

    ##############################
    # Create partner user
    user_pk = str(uuid.uuid4())
    partner_user = {
        "user_pk": user_pk,
        "user_name": "John",
        "user_last_name": "Partner",
        "user_street": "Nørrebrogade 2",
        "user_postalcode": 2200,
        "user_city": "København",
        "user_email": "partner@company.com",
        "user_password": generate_password_hash("password"),
        "user_created_at": int(time.time()),
        "user_deleted_at": 0,
        "user_blocked_at": 0,
        "user_updated_at": 0,
        "user_verified_at": int(time.time()),
        "user_verification_key": str(uuid.uuid4()),
        "user_reset_password_key": 0
    }
    insert_user(partner_user)

    # Insert partner role
    cursor.execute("""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) 
        VALUES (%s, %s)
    """, (user_pk, x.PARTNER_ROLE_PK))

    ##############################
    # Create customer user
    user_pk = str(uuid.uuid4())
    customer_user = {
        "user_pk": user_pk,
        "user_name": "John",
        "user_last_name": "Customer",
        "user_street": "Nørrebrogade 2",
        "user_postalcode": 2200,
        "user_city": "København",
        "user_email": "customer@company.com",
        "user_password": generate_password_hash("password"),
        "user_created_at": int(time.time()),
        "user_deleted_at": 0,
        "user_blocked_at": 0,
        "user_updated_at": 0,
        "user_verified_at": int(time.time()),
        "user_verification_key": str(uuid.uuid4()),
        "user_reset_password_key": 0
    }
    insert_user(customer_user)

    # Insert customer role
    cursor.execute("""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) 
        VALUES (%s, %s)
    """, (user_pk, x.CUSTOMER_ROLE_PK))




    ############################## 
    # Create 50 customers
    for _ in range(49):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user_verification_key = str(uuid.uuid4())
        user = {
            "user_pk" : user_pk,
            "user_name" : fake.first_name(),
            "user_last_name" : fake.last_name(),
            "user_street": fake.street_address(),
            "user_postalcode": random.randint(1000, 2450),
            "user_city": "København",
            "user_email" : fake.unique.email(),
            "user_password" : generate_password_hash("password"),
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : user_verification_key,
            "user_reset_password_key": 0
        }
        insert_user(user)

        cursor.execute("""
        INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)
        """, (user_pk, x.CUSTOMER_ROLE_PK))



    ############################## 
    # Create 50 partners
    for _ in range(49):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user_verification_key = str(uuid.uuid4())
        user = {
            "user_pk" : user_pk,
            "user_name" : fake.first_name(),
            "user_last_name" : fake.last_name(),
            "user_street": fake.street_address(),
            "user_postalcode": random.randint(1000, 2450),
            "user_city": "København",
            "user_email" : fake.unique.email(),
            "user_password" : generate_password_hash("password"),
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : user_verification_key,
            "user_reset_password_key": 0
        }
        insert_user(user)

        cursor.execute("""
        INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)
        """, (user_pk, x.PARTNER_ROLE_PK))


    # Commit all changes at once
    db.commit()

    print("Data inserted successfully!")

except Exception as ex:
    print(f"An error occurred: {ex}")
    db.rollback()  # Rollback changes in case of any error

finally:
    # Always close the cursor and connection
    cursor.close()
    db.close()
