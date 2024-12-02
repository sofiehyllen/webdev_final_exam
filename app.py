from flask import Flask, session, render_template, redirect, url_for, make_response, request
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x
import uuid 
import time
import redis
import os

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis', etc.
Session(app)


# app.secret_key = "your_secret_key"

##############################
##############################
##############################

def _________GET_________(): pass

##############################
##############################
##############################



@app.get("/test-set-redis")
def view_test_set_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
    redis_client.set("name", "Santiago", ex=10)
    return "name saved"

@app.get("/test-get-redis")
def view_test_get_redis():
    redis_host = "redis"
    redis_port = 6379
    redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)    
    name = redis_client.get("name")
    if not name: name = "no name"
    return name



##############################
@app.get("/")
def view_index():
    return render_template("view_index.html")



##############################
@app.get("/signup")
@x.no_cache
def view_signup():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_signup.html", x=x, title="Signup")



##############################
@app.get("/signup_restaurant")
@x.no_cache
def view_signup_restaurant():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "restaurant" in session.get("user").get("roles"):
            return redirect(url_for("view_restaurant"))         
    return render_template("view_signup_restaurant.html", x=x, title="Signup Restaurant")



##############################
@app.get("/login")
@x.no_cache
def view_login():  
    ic(session)
    # print(session, flush=True)  
    if session.get("account"):
        if len(session.get("account").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("account").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("account").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("account").get("roles"):
            return redirect(url_for("view_partner"))         
        if "restaurant" in session.get("account").get("roles"):
            return redirect(url_for("view_restaurant"))         
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))



##############################
@app.get("/customer")
@x.no_cache
def view_customer():
    if not session.get("account", ""): 
        return redirect(url_for("view_login"))
    user = session.get("account")
    # if len(user.get("roles", "")) > 1:
    #     return redirect(url_for("view_choose_role"))
    return render_template("view_customer.html", user=user)



##############################
@app.get("/customer/items")
@x.no_cache
def view_customer_items():
    try:
        if not session.get("account", ""): 
            return redirect(url_for("view_login"))
        user = session.get("account")
        if len(user.get("roles", "")) > 1:
            return redirect(url_for("view_choose_role"))

        db, cursor = x.db()
        q = 'SELECT * FROM items'
        cursor.execute(q)
        items = cursor.fetchall()

        return render_template("view_customer_items.html", user=user, items=items)
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("account", ""): 
        return redirect(url_for("view_login"))
    user = session.get("account")
    # if len(user.get("roles", "")) > 1:
    #     return redirect(url_for("view_choose_role"))
    if not "partner" in user.get("roles", ""):
        return redirect(url_for("view_login"))
    return render_template("view_partner.html", user=user)


##############################
@app.get("/admin")
@x.no_cache
def view_admin():
    if not session.get("account", ""): 
        return redirect(url_for("view_login"))
    user = session.get("account")
    if not "admin" in user.get("roles", ""):
        return redirect(url_for("view_login"))
    return render_template("view_admin.html", user=user)



##############################
@app.get("/admin/users")
def view_admin_users():
    try:
        # Ensure the user is an admin
        if not session.get("account", ""): 
            return redirect(url_for("view_login"))
        user = session.get("account")
        if not "admin" in user.get("roles", ""):
            return redirect(url_for("view_login"))
        
        # Connect to DB and fetch users
        db, cursor = x.db()
        q = 'SELECT account_pk, account_name, account_email, account_blocked_at, account_deleted_at, account_roles FROM accounts'
        cursor.execute(q)
        accounts = cursor.fetchall()

        return render_template('view_admin_users.html', user=user, accounts=accounts)

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/restaurant")
@x.no_cache
def view_restaurant():
    if not session.get("account", ""): 
        return redirect(url_for("view_login"))
    user = session.get("account")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    if not "restaurant" in user.get("roles", ""):
        return redirect(url_for("view_login"))    
    return render_template("view_restaurant.html", user=user)



@app.get("/restaurant/create-item")
@x.no_cache
def view_restaurant_create_item():
    if not session.get("account", ""): 
        return redirect(url_for("view_login"))
    user = session.get("account")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    if not "restaurant" in user.get("roles", ""):
        return redirect(url_for("view_login"))  
    return render_template("view_restaurant_create_item.html", user=user, x=x)



##############################
@app.get("/choose-role")
@x.no_cache
def view_choose_role():
    if not session.get("account", ""): 
        return redirect(url_for("view_login"))
    if not len(session.get("account").get("roles")) >= 2:
        return redirect(url_for("view_login"))
    user = session.get("account")
    return render_template("view_choose_role.html", user=user, title="Choose role")



##############################
@app.get("/forgot-password")
@x.no_cache
def view_forgot_password():
    return render_template("view_forgot_password.html", x=x, title="Forgot password")



##############################
@app.get("/reset-password/<reset_password_key>")
@x.no_cache
def view_reset_password(reset_password_key):
    if not reset_password_key:
        return redirect(url_for("view_login"))
    return render_template("view_reset_password.html", x=x, reset_password_key=reset_password_key, title="Reset password")



##############################
@app.get("/edit-profile")
def view_edit_profile():
    if not session.get("account", ""): 
        return redirect(url_for("view_login"))
    user = session.get("account")
    return render_template("view_edit_profile.html", user=user, x=x)



##############################
@app.get("/edit-restaurant-profile")
def view_edit_restaurant_profile():
    if not session.get("account", ""): 
        return redirect(url_for("view_login"))
    user = session.get("account")
    return render_template("view_edit_restaurant_profile.html", user=user, x=x)




##############################
##############################
##############################

def _________POST_________(): pass

##############################
##############################
##############################

@app.post("/logout")
def logout():
    # ic("#"*30)
    # ic(session)
    session.pop("account", None)
    # session.clear()
    # session.modified = True
    # ic("*"*30)
    # ic(session)
    return redirect(url_for("view_login"))


##############################
@app.post("/users")
@x.no_cache
def signup():
    try:
        selected_role = x.validate_user_role() 
        user_name = x.validate_account_name("user_name")
        user_last_name = x.validate_account_name("user_last_name")
        user_email = x.validate_account_email("user_email")
        user_password = x.validate_account_password("user_password")
        hashed_password = generate_password_hash(user_password)
        
        user_pk = str(uuid.uuid4())
        user_created_at = int(time.time())
        user_deleted_at = 0
        user_blocked_at = 0
        user_updated_at = 0
        user_verified_at = 0
        account_verification_key = str(uuid.uuid4())

        db, cursor = x.db()

        q_check_email = """
        SELECT 'exists' FROM accounts WHERE account_email = %s
        """
        cursor.execute(q_check_email, (user_email,))
        result = cursor.fetchone()
        
        if result:
            toast = render_template("___toast.html", message="Email not available")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400

        cursor.execute('SELECT role_pk FROM roles WHERE role_name = %s', (selected_role,))

        result = cursor.fetchone()
        
        if not result:
                    return "Role not found", 404

        user_role = result["role_pk"]

        q = '''
            INSERT INTO users 
            (user_pk, user_name, user_last_name, user_email, user_password, user_created_at, 
            user_deleted_at, user_blocked_at, user_updated_at, user_verified_at, user_verification_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        cursor.execute(q, (user_pk, user_name, user_last_name, user_email, 
                            hashed_password, user_created_at, user_deleted_at, user_blocked_at, 
                            user_updated_at, user_verified_at, account_verification_key))

        
        q_roles = 'INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES (%s, %s)'
        cursor.execute(q_roles, (user_pk, user_role))

        x.send_verify_email(user_email, account_verification_key)

        db.commit()
    
        return """<template mix-redirect="/login"></template>""", 201
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "users.user_email" in str(ex): 
                toast = render_template("___toast.html", message="email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            return f"""<template mix-target="#toast" mix-bottom>System upgrating</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.post("/restaurants")
@x.no_cache
def signup_restaurant():
    try:
        restaurant_name = x.validate_account_name("restaurant_name")
        restaurant_email = x.validate_account_email("restaurant_email")
        restaurant_password = x.validate_account_password("restaurant_password")
        hashed_password = generate_password_hash(restaurant_password)
        
        restaurant_pk = str(uuid.uuid4())
        restaurant_created_at = int(time.time())
        restaurant_deleted_at = 0
        restaurant_blocked_at = 0
        restaurant_updated_at = 0
        restaurant_verified_at = 0
        account_verification_key = str(uuid.uuid4())

        db, cursor = x.db()

        q_check_email = """
        SELECT 'exists' FROM accounts WHERE account_email = %s
        """
        cursor.execute(q_check_email, (restaurant_email,))
        result = cursor.fetchone()
        
        if result:
            toast = render_template("___toast.html", message="Email not available")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400


        q = '''
            INSERT INTO restaurants 
            (restaurant_pk, restaurant_name, restaurant_email, restaurant_password, restaurant_created_at, 
            restaurant_deleted_at, restaurant_blocked_at, restaurant_updated_at, restaurant_verified_at, restaurant_verification_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        cursor.execute(q, (restaurant_pk, restaurant_name, restaurant_email, 
                            hashed_password, restaurant_created_at, restaurant_deleted_at, restaurant_blocked_at, 
                            restaurant_updated_at, restaurant_verified_at, account_verification_key))

        
        x.send_verify_email(restaurant_email, account_verification_key)

        db.commit()
    
        return """<template mix-redirect="/login"></template>""", 201
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "restaurants.restaurant_email" in str(ex): 
                toast = render_template("___toast.html", message="email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            return f"""<template mix-target="#toast" mix-bottom>System upgrating</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
@app.post("/login")
def login():
    try:
        account_email = x.validate_account_email("user_email")
        account_password = x.validate_account_password("user_password")

        db, cursor = x.db()

        # Query the accounts view to check both users and restaurants
        query = """
            SELECT account_pk, account_name, account_email,
            account_password, account_verified_at, account_roles,
            user_last_name, account_deleted_at
            FROM accounts
            LEFT JOIN users ON accounts.account_pk = users.user_pk
            WHERE account_email = %s
        """
        cursor.execute(query, (account_email,))
        rows = cursor.fetchall()

        # If no account is found, return an error
        if not rows:
            toast = render_template("___toast.html", message="Account not registered")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        # Validate password
        if not check_password_hash(rows[0]["account_password"], account_password):
            toast = render_template("___toast.html", message="Invalid credentials")
            return f"""<template mix-target="#toast">{toast}</template>""", 401

        # Verify account
        if not rows[0]["account_verified_at"]:
            toast = render_template("___toast.html", message="Account not verified")
            return f"""<template mix-target="#toast">{toast}</template>""", 403
        
        # Check if account is deleted
        if rows[0]["account_deleted_at"]:
            toast = render_template("___toast.html", message="Account deleted")
            return f"""<template mix-target="#toast">{toast}</template>""", 403
        

        ic(rows[0])
        # Process roles
        roles = rows[0]["account_roles"].split(', ')

        account = {
            "account_pk": rows[0]["account_pk"],
            "account_name": rows[0]["account_name"],
            "account_last_name": rows[0].get("user_last_name"),
            "account_email": rows[0]["account_email"],
            "account_deleted_at": rows[0]["account_deleted_at"],
            "roles": roles,
        }

        ic(account)
        session["account"] = account

        # Redirect based on roles
        if len(roles) == 1:
            return f"""<template mix-redirect="/{roles[0]}"></template>"""
        return f"""<template mix-redirect="/choose-role"></template>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500
        return "<template>System under maintenance</template>", 500
    finally:
        if "cursor" in locals():
            cursor.close()
        if "db" in locals():
            db.close()


##############################
@app.post("/forgot-password")
def forgot_password():
    try:
        account_email = x.validate_account_email("user_email")  # Unified email validation for both users and restaurants
        account_reset_password_key = str(uuid.uuid4())

        db, cursor = x.db()

        # Query the accounts view for both users and restaurants
        accounts_query = """
            SELECT account_pk, account_email, account_roles, account_verified_at
            FROM accounts
            WHERE account_email = %s
        """
        cursor.execute(accounts_query, (account_email,))
        account = cursor.fetchone()

        if not account:
            toast = render_template("___toast.html", message="Account not registered")
            return f"""<template mix-target="#toast">{toast}</template>""", 400

        if not account["account_verified_at"]:
            toast = render_template("___toast.html", message="Account not verified")
            return f"""<template mix-target="#toast">{toast}</template>""", 403

        if account["account_roles"] == "restaurant":
            update_query = """
                UPDATE restaurants
                SET restaurant_reset_password_key = %s
                WHERE restaurant_email = %s
            """            
        else:
            update_query = """
                UPDATE users
                SET user_reset_password_key = %s
                WHERE user_email = %s
            """

        cursor.execute(update_query, (account_reset_password_key, account_email))
        db.commit()

        x.send_reset_password_email(account_email, account_reset_password_key)

        return """<template mix-redirect="/login"></template>""", 201

    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500
        return "<template>System under maintenance</template>", 500
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.post("/reset-password/<reset_password_key>")
@x.no_cache
def reset_password(reset_password_key):
    try:
        reset_password_key = x.validate_uuid4(reset_password_key)
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        if new_password != confirm_password:
            toast = render_template("___toast.html", message="Passwords don't match")
            return f"""<template mix-target="#toast">{toast}</template>""", 400
        
        hashed_password = generate_password_hash(new_password)

        db, cursor = x.db()

        # Try resetting password for users
        user_query = """
            UPDATE users
            SET user_password = %s, user_updated_at = %s, user_reset_password_key = 0
            WHERE user_reset_password_key = %s
        """
        cursor.execute(user_query, (hashed_password, int(time.time()), reset_password_key))

        if cursor.rowcount == 1:  # Found and updated in 'users'
            db.commit()
            return """<template mix-redirect="/login"></template>""", 201

        # Try resetting password for restaurants
        restaurant_query = """
            UPDATE restaurants
            SET restaurant_password = %s, restaurant_updated_at = %s, restaurant_reset_password_key = 0
            WHERE restaurant_reset_password_key = %s
        """
        cursor.execute(restaurant_query, (hashed_password, int(time.time()), reset_password_key))

        if cursor.rowcount == 1:  # Found and updated in 'restaurants'
            db.commit()
            return """<template mix-redirect="/login"></template>""", 201

        x.raise_custom_exception("Invalid or expired reset key", 400)

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return ex.message, ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "Database under maintenance", 500        
        return "System under maintenance", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()  



##############################
@app.post("/items")
def create_item():
    try:
        item_title = x.validate_account_name("item_title")
        item_description = x.validate_item_description()
        item_price = x.validate_item_price()
        
        item_pk = str(uuid.uuid4())
        item_created_at = int(time.time())
        item_deleted_at = 0
        item_blocked_at = 0
        item_updated_at = 0
        item_restaurant_fk = session.get("account").get("account_pk")


        # TODO: raise toast if price is not correct

        db, cursor = x.db()

        q = '''
            INSERT INTO items (
                item_pk, 
                item_title, 
                item_description, 
                item_price, 
                item_created_at, 
                item_deleted_at, 
                item_blocked_at, 
                item_updated_at,
                item_restaurant_fk
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(q, (
            item_pk, 
            item_title, 
            item_description, 
            item_price, 
            item_created_at, 
            item_deleted_at, 
            item_blocked_at, 
            item_updated_at,
            item_restaurant_fk
        ))

        #TODO: add multiple files one at a time

        valid_files = x.validate_item_image() 
        
        for file, item_image_name in valid_files:
            print(request.files.getlist("item_image_name"))

            # Save the image to the server
            image_path = os.path.join(x.UPLOAD_ITEM_FOLDER, item_image_name)
            file.save(image_path)

            item_image_pk = str(uuid.uuid4())

            image_q = '''
                INSERT INTO item_images (
                    item_image_pk, 
                    item_image_item_fk, 
                    item_image_name
                ) VALUES (%s, %s, %s)
            '''
            cursor.execute(image_q, (
                item_image_pk,
                item_pk, 
                item_image_name  
            ))

        db.commit()

        #TODO: clear form when item created

        toast = render_template("___toast.html", message="Item has been created")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()    


##############################
##############################
##############################

def _________PUT_________(): pass

##############################
##############################
##############################

@app.put("/users")
def user_update():
    try:
        user_pk = session.get("account").get("account_pk")
        user_name = x.validate_account_name("user_name")
        user_last_name = x.validate_account_name("user_last_name")
        user_email = x.validate_account_email("user_email")
        user_updated_at = int(time.time())

        db, cursor = x.db()
        
        # Fetch the current user info
        cursor.execute(
            """ SELECT user_name, user_last_name, user_email, user_verified_at, user_verification_key 
                FROM users 
                WHERE user_pk = %s""", (user_pk,))
        current_user = cursor.fetchone()
        if not current_user:
            x.raise_custom_exception("user not found", 404)

        if current_user["user_email"] != user_email:
            q_check_email = """
            SELECT 'exists' FROM accounts WHERE account_email = %s
            """
            cursor.execute(q_check_email, (user_email,))
            result = cursor.fetchone()
            
            if result:
                toast = render_template("___toast.html", message="Email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400

        if (
            current_user["user_name"] == user_name and
            current_user["user_last_name"] == user_last_name and
            current_user["user_email"] == user_email ):
            
            toast = render_template("___toast.html", message="No changes made")
            return f"""<template mix-target="#toast">{toast}</template>"""
        
        user_verified_at = 0 if current_user["user_email"] != user_email else current_user["user_verified_at"]

        cursor.execute(
            """UPDATE users SET user_name = %s, user_last_name = %s, 
            user_email = %s, user_updated_at = %s, user_verified_at = %s 
            WHERE user_pk = %s""",
            (user_name, user_last_name, user_email, user_updated_at, user_verified_at, user_pk))
        if cursor.rowcount != 1: 
            x.raise_custom_exception("cannot update user", 401)

        db.commit()

        session["account"].update({
            "account_name": user_name, 
            "account_last_name": user_last_name, 
            "account_email": user_email
        })

        if current_user["user_email"] != user_email:
            x.send_verify_email(user_email, current_user["user_verification_key"])
            toast = render_template("___toast.html", message="Email send to verify your new email address")
        else:
            toast = render_template("___toast.html", message="Profile has been updated")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""
        
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code
        
        if isinstance(ex, x.mysql.connector.Error):
            if "users.user_email" in str(ex): 
                return "<template>email not available</template>", 400
            return "<template>System upgrading</template>", 500        
        
        return "<template>System under maintenance</template>", 500    

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.put("/restaurants")
def restaurant_update():
        try:
            restaurant_pk = session.get("account").get("account_pk")
            restaurant_name = x.validate_account_name("user_name")
            restaurant_email = x.validate_account_email("user_email")
            restaurant_updated_at = int(time.time())

            db, cursor = x.db()

            cursor.execute(
                """ SELECT restaurant_name, restaurant_email, restaurant_verified_at, restaurant_verification_key 
                    FROM restaurants 
                    WHERE restaurant_pk = %s""", (restaurant_pk,))
            current_user = cursor.fetchone()
            if not current_user:
                x.raise_custom_exception("user not found", 404)
    
            if current_user["restaurant_email"] != restaurant_email:
                q_check_email = """
                SELECT 'exists' FROM accounts WHERE account_email = %s
                """
                cursor.execute(q_check_email, (restaurant_email,))
                result = cursor.fetchone()
            
                if result:
                    toast = render_template("___toast.html", message="Email not available")
                    return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
                
            if (
                current_user["restaurant_name"] == restaurant_name and
                current_user["restaurant_email"] == restaurant_email ):
                
                toast = render_template("___toast.html", message="No changes made")
                return f"""<template mix-target="#toast">{toast}</template>"""
            
            restaurant_verified_at = 0 if current_user["restaurant_email"] != restaurant_email else current_user["restaurant_verified_at"]

            cursor.execute(
                """UPDATE restaurants SET restaurant_name = %s, restaurant_email = %s, 
                    restaurant_updated_at = %s, restaurant_verified_at = %s 
                WHERE restaurant_pk = %s""",
                (restaurant_name, restaurant_email, restaurant_updated_at, restaurant_verified_at, restaurant_pk))
            if cursor.rowcount != 1: 
                x.raise_custom_exception("cannot update user", 401)

            db.commit()

            session["account"].update({
                "account_name": restaurant_name, 
                "account_email": restaurant_email
            })

            if current_user["restaurant_email"] != restaurant_email:
                x.send_verify_email(restaurant_email, current_user["restaurant_verification_key"])
                toast = render_template("___toast.html", message="Email send to verify your new email address")
            else:
                toast = render_template("___toast.html", message="Profile has been updated")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""
            
        
        except Exception as ex:
            ic(ex)
            if "db" in locals(): db.rollback()
            if isinstance(ex, x.CustomException):
                return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code
            
            if isinstance(ex, x.mysql.connector.Error):
                ic(ex)
                if "users.user_email" in str(ex):
                    return """<template mix-target="#toast" mix-bottom>email not available</template>""", 400
                return "<template>System upgrading</template>", 500  

            return """<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500  
        
        finally:
            if "cursor" in locals(): cursor.close()
            if "db" in locals(): db.close()
    


##############################
@app.put("/users/block/<account_pk>")
def user_block(account_pk):
    try:        

        account_pk = x.validate_uuid4(account_pk)
        account_blocked_at = int(time.time())

        db, cursor = x.db()

        q = 'SELECT account_email FROM accounts WHERE account_pk = %s'
        cursor.execute(q, (account_pk,))
        account = cursor.fetchone()
        if not account: 
            x.raise_custom_exception("user not found", 404)

        account_email = account["account_email"]

        q = '''
            UPDATE users 
            SET user_blocked_at = %s 
            WHERE user_pk = %s
        '''
        cursor.execute(q, (account_blocked_at, account_pk))
        if cursor.rowcount != 1: 
            q = '''
                UPDATE restaurants 
                SET restaurant_blocked_at = %s 
                WHERE restaurant_pk = %s
            '''
            cursor.execute(q, (account_blocked_at, account_pk))
            if cursor.rowcount != 1:
                x.raise_custom_exception("cannot block account", 400)

        db.commit()

        x.send_block_email(account_email)

        unblock_html = render_template("___btn_unblock.html", account_pk=account_pk)
        toast = render_template("___toast.html", message = "User blocked")

        return f"""
                <template mix-target="#block-user-{ account_pk }" mix-replace>
                    {unblock_html}
                </template>
                <template mix-target="#toast" mix-top>
                    {toast}
                </template>                
            """
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
@app.put("/users/unblock/<account_pk>")
def user_unblock(account_pk):
    try:

        account_pk = x.validate_uuid4(account_pk)
        account_blocked_at = 0

        db, cursor = x.db()

        q = '''
            UPDATE users 
            SET user_blocked_at = %s 
            WHERE user_pk = %s
        '''
        cursor.execute(q, (account_blocked_at, account_pk))
        
        # If no rows are affected, try the 'restaurants' table
        if cursor.rowcount != 1:
            q = '''
                UPDATE restaurants 
                SET restaurant_blocked_at = %s 
                WHERE restaurant_pk = %s
            '''
            cursor.execute(q, (account_blocked_at, account_pk))
            if cursor.rowcount != 1:
                x.raise_custom_exception("cannot unblock account", 400)
        
        db.commit()

        block_html = render_template("___btn_block.html", account_pk=account_pk)
        toast = render_template("___toast.html", message = "User unblocked")
        return f"""
                <template mix-target="#unblock-user-{ account_pk }" mix-replace>
                    {block_html}
                </template>
                <template mix-target="#toast" mix-top>
                    {toast}
                </template>                
            """
    
    except Exception as ex:

        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
##############################
##############################

def _________DELETE_________(): pass

##############################
##############################
##############################


@app.delete("/admin/users/delete/<account_pk>")
def admin_user_delete(account_pk):
    try:
        if not session.get("account", ""): return redirect(url_for("view_login"))
        if not "admin" in session.get("account").get("roles"): return redirect(url_for("view_login"))

        account_pk = x.validate_uuid4(account_pk)
        account_deleted_at = int(time.time())

        db, cursor = x.db()

        query = "SELECT account_roles FROM accounts WHERE account_pk = %s"
        cursor.execute(query, (account_pk,))
        row = cursor.fetchone()
        ic(row)
        if not row: 
            x.raise_custom_exception("Account not found", 400)
        else: 
            account_roles = row["account_roles"]

        if account_roles in ["customer", "partner"]:
            q_users = "UPDATE users SET user_deleted_at = %s WHERE user_pk = %s"
            cursor.execute(q_users, (account_deleted_at, account_pk))
        elif account_roles == "restaurant":
            q_restaurants = "UPDATE restaurants SET restaurant_deleted_at = %s WHERE restaurant_pk = %s"
            cursor.execute(q_restaurants, (account_deleted_at, account_pk))

        else:
            x.raise_custom_exception("Invalid account role. No update performed.", 400)

        db.commit()

        deleted_at_html = render_template(
            "___deleted_at.html", account_deleted_at=account_deleted_at
        )

        toast = render_template("___toast.html", message = "User deleted")
        return f"""
                <template mix-target="#delete-user-btn-{account_pk}" mix-replace>
                    {deleted_at_html}
                </template>
                <template mix-target="#toast" mix-bottom>
                    {toast}
                </template>                
            """
    
    except Exception as ex:

        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



@app.delete("/users/delete/<account_pk>")
def user_delete(account_pk):
    try:
        account_pk = x.validate_uuid4(account_pk)
        account_deleted_at = int(time.time())

        db, cursor = x.db()

        account_roles = session.get("account").get("roles")

        if account_roles in ["customer", "partner"]:
            q_users = "UPDATE users SET user_deleted_at = %s WHERE user_pk = %s"
            cursor.execute(q_users, (account_deleted_at, account_pk))
        elif account_roles == "restaurant":
            q_restaurants = "UPDATE restaurants SET restaurant_deleted_at = %s WHERE restaurant_pk = %s"
            cursor.execute(q_restaurants, (account_deleted_at, account_pk))
        else:
            x.raise_custom_exception("Invalid account role. No update performed.", 400)

        db.commit()

        return f"""
                <template mix-target="" mix-bottom>
                </template>"""
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
##############################
##############################

def _________BRIDGE_________(): pass

##############################
##############################
##############################


##############################
@app.get("/verify/<verification_key>")
@x.no_cache
def verify_user(verification_key):
    try:
        ic(verification_key)
        verification_key = x.validate_uuid4(verification_key)

        db, cursor = x.db()

        user_query = """ 
            UPDATE users 
            SET user_verified_at = %s 
            WHERE user_verification_key = %s
        """
        cursor.execute(user_query, (int(time.time()), verification_key))

        if cursor.rowcount == 1:
            db.commit()
            return redirect(url_for("view_login", message="User verified, please login"))

        restaurant_query = """ 
            UPDATE restaurants 
            SET restaurant_verified_at = %s 
            WHERE restaurant_verification_key = %s
        """
        cursor.execute(restaurant_query, (int(time.time()), verification_key))

        if cursor.rowcount == 1:
            db.commit()
            return redirect(url_for("view_login", message="Restaurant verified, please login"))

        x.raise_custom_exception("Cannot verify account", 400)

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): return ex.message, ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "Database under maintenance", 500        
        return "System under maintenance", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()    
