from flask import Flask, session, render_template, redirect, url_for, make_response, request, jsonify
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from x import redis_client
import decimal
import x
import uuid 
import time
import os
import json


from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="webdev_final_exam")

load_dotenv()

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



##############################
@app.get("/")
def view_index():    
    return render_template("view_index.html")



##############################
@app.get("/signup")
@x.no_cache
def view_signup():  
    user = session.get("account")
    if user:
        roles = user.get("roles", [])
        if "customer" in roles:
            return redirect(url_for("view_customer"))
        if "admin" in roles:
            return redirect(url_for("view_admin"))
        if "partner" in roles:
            return redirect(url_for("view_partner"))
        if "restaurant" in roles:
            return redirect(url_for("view_restaurant"))       
        if len(roles) > 1:
            return redirect(url_for("view_choose_role"))
    return render_template("view_signup.html", x=x, title="Signup")



##############################
@app.get("/signup_restaurant")
@x.no_cache
def view_signup_restaurant():  
    user = session.get("account")
    if user:
        roles = user.get("roles", [])
        if "customer" in roles:
            return redirect(url_for("view_customer"))
        if "admin" in roles:
            return redirect(url_for("view_admin"))
        if "partner" in roles:
            return redirect(url_for("view_partner"))
        if "restaurant" in roles:
            return redirect(url_for("view_restaurant"))       
        if len(roles) > 1:
            return redirect(url_for("view_choose_role"))    
    return render_template("view_signup_restaurant.html", x=x, title="Signup Restaurant")



##############################
@app.get("/login")
@x.no_cache
def view_login():  
    user = session.get("account")
    if user:
        roles = user.get("roles", [])
        if "customer" in roles:
            return redirect(url_for("view_customer"))
        if "admin" in roles:
            return redirect(url_for("view_admin"))
        if "partner" in roles:
            return redirect(url_for("view_partner"))
        if "restaurant" in roles:
            return redirect(url_for("view_restaurant"))       
        if len(roles) > 1:
            return redirect(url_for("view_choose_role"))          
    return render_template("view_login.html", x=x, title="Login", message=request.args.get("message", ""))



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
@app.get("/choose-role")
@x.no_cache
def view_choose_role():
    user = session.get("account")
    if not user: 
        return redirect(url_for("view_login"))
    if not len(user.get("roles")) >= 2:
        return redirect(url_for("view_login"))
    return render_template("view_choose_role.html", user=user, title="Choose role")



##############################
@app.get("/customer")
@x.require_role("customer")
@x.no_cache
def view_customer(role=None):
    user = session.get("account", "")
    address = get_restaurants_data()
    basket_quantity = get_basket_and_quantity(user.get('account_pk'))
    return render_template("view_customer.html", user=user, address=address, role=role, basket_quantity=basket_quantity)



##############################
@app.get("/partner")
@x.require_role("partner")
@x.no_cache
def view_partner(role=None):
    user = session.get("account", "")
    return render_template("view_partner.html", user=user, role=role)



##############################
@app.get("/restaurant")
@x.no_cache
def view_restaurant():
    user = session.get("account")
    if not 'restaurant' in user.get("roles"):
        return redirect(url_for("view_login"))
    return render_template("view_restaurant.html", user=user)



##############################
@app.get("/admin")
@x.no_cache
def view_admin():
    user = session.get("account")
    if not 'admin' in user.get("roles"):
        return redirect(url_for("view_login"))
    return render_template("view_admin.html", user=user)



##############################
def get_restaurants_data(limit=None, offset=None):
    try:
        db, cursor = x.db()
        
        q = """
            SELECT 
                restaurant_pk, 
                restaurant_name, 
                restaurant_street, 
                restaurant_postalcode, 
                restaurant_city, 
                restaurant_email,
                restaurant_image_name, 
                restaurant_latitude, 
                restaurant_longitude 
            FROM restaurants
            WHERE restaurant_deleted_at = 0"""

        if limit is not None and offset is not None:
            q += f" LIMIT {limit} OFFSET {offset}"
    
        cursor.execute(q)
        all_restaurants = cursor.fetchall()

        if not all_restaurants:
            x.raise_custom_exception("no data for table restaurants available", 404)

        return all_restaurants
    
    except Exception as ex:
        ic(ex)
        if "db" in locals():
            db.rollback()
        if isinstance(ex, x.CustomException):
            return f"""<template>{ex.message}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500
        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()







##############################
@app.get("/map-locations")
def get_map_locations():
    try:
        addresses = get_restaurants_data()
        locations = []

        for address in addresses:
            restaurant_pk = address["restaurant_pk"]
            restaurant_name = address["restaurant_name"]
            restaurant_image_name = address["restaurant_image_name"]
            latitude = address["restaurant_latitude"]
            longitude = address["restaurant_longitude"]

            popup_html = render_template(
                '___map_popup.html',
                restaurant_name=restaurant_name,
                restaurant_image_name=restaurant_image_name,
                restaurant_pk=restaurant_pk
            )

            locations.append({
                "coords": [latitude, longitude] if latitude and longitude else [None, None],
                "popup": popup_html
            })

        return jsonify(locations)
    
    except Exception as ex:
        ic(ex)
        return "<template>System under maintenance</template>", 500






##############################
@app.get("/customer/restaurants")
@x.require_role("customer")
@x.no_cache
def view_all_restaurants(role=None):
    try:
        user = session.get("account")
        basket_quantity = get_basket_and_quantity(user.get('account_pk'))

        db, cursor = x.db()
        q = """
                SELECT 
                restaurant_pk, 
                restaurant_name, 
                restaurant_street,
                restaurant_postalcode,
                restaurant_city,
                restaurant_image_name 
                FROM restaurants 
                WHERE restaurant_deleted_at = 0
                LIMIT 0,6"""
        cursor.execute(q)
        restaurants = cursor.fetchall()

        next_page = 2

        return render_template("view_all_restaurants.html", user=user, restaurants=restaurants, next_page=next_page, table_name="restaurants", role=role, basket_quantity=basket_quantity)
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
@app.get("/order-confirmation")
@x.require_role("customer")
@x.no_cache
def view_order_confirmation(role=None):
    user = session.get("account")
    basket_quantity = get_basket_and_quantity(user.get('account_pk'))
    return render_template("view_order_confirmation.html", user=user, role=role, basket_quantity=basket_quantity)



def fetch_items(query, params=None):
    try:
        db, cursor = x.db()
        cursor.execute(query, params)
        items = cursor.fetchall()

        for item in items:
            item['item_image_names'] = item['item_image_names'].split(',') if item['item_image_names'] else []

        return items

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return ic(ex.message)
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


@app.get("/customer/items")
@x.require_role('customer')
@x.no_cache
def view_all_items(role=None):
    try:
        user = session.get("account")
        basket_quantity = get_basket_and_quantity(user.get('account_pk'))

        query = '''
            SELECT 
                i.item_pk, 
                i.item_title, 
                i.item_description, 
                i.item_price, 
                GROUP_CONCAT(ii.item_image_name) AS item_image_names
            FROM items i
            LEFT JOIN item_images ii ON i.item_pk = ii.item_image_item_fk
            WHERE i.item_deleted_at = 0
            GROUP BY i.item_pk, i.item_title, i.item_description, i.item_price
            LIMIT 0,6
        '''
        
        items = fetch_items(query)

        next_page = 2

        return render_template("view_all_items.html", user=user, items=items, x=x, next_page=next_page, table_name="items", role=role, basket_quantity=basket_quantity)
    
    except Exception as ex:
        ic(ex)
        return "<template>System under maintenance</template>", 500


def get_item_by_pk(item_pk):
    try:
        item_pk = x.validate_uuid4(item_pk)

        query = '''
            SELECT 
                i.item_pk, 
                i.item_title, 
                i.item_description, 
                i.item_price, 
                GROUP_CONCAT(ii.item_image_name) AS item_image_names
            FROM items i
            LEFT JOIN item_images ii ON i.item_pk = ii.item_image_item_fk
            WHERE i.item_deleted_at = 0 AND i.item_pk = %s
            GROUP BY i.item_pk, i.item_title, i.item_description, i.item_price
        '''
        
        items = fetch_items(query, (item_pk,))
        if not items:
            x.raise_custom_exception("Item not found")

        return items[0]  # Only one item expected
    
    except Exception as ex:
        ic(ex)
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        return "<template>System under maintenance</template>", 500




def get_items_from_basket(basket):
    try:
        # Extract only item_pk values from the basket
        item_pks = [item['item_pk'] for item in basket if 'item_pk' in item]

        # Check if there are any items to query
        if not item_pks:
            return []

        # Create placeholders for SQL query
        placeholders = ', '.join(['%s'] * len(item_pks))
        db, cursor = x.db()
        # Construct the query to fetch item details
        query = f'''
            SELECT i.item_pk, i.item_title, i.item_description, i.item_price, 
                    GROUP_CONCAT(ii.item_image_name) AS item_image_names
            FROM items i
            LEFT JOIN item_images ii ON i.item_pk = ii.item_image_item_fk
            WHERE i.item_deleted_at = 0 AND i.item_pk IN ({placeholders})
            GROUP BY i.item_pk
        '''

        # Execute the query with item_pks
        cursor.execute(query, tuple(item_pks))
        items = cursor.fetchall()

        # Build the result including quantities from the basket
        result = []
        for item in items:
            item['item_image_names'] = item['item_image_names'].split(',') if item['item_image_names'] else []
            quantity = next((b['quantity'] for b in basket if b['item_pk'] == item['item_pk']), 0)
            item['quantity'] = quantity
            result.append(item)

        return result
    
    except Exception as ex:
        ic(ex)
        return []  # Return an empty list if there's an error





def get_basket_and_quantity(user_pk):
    basket = redis_client.get(user_pk)
    
    # If basket exists and is not None, deserialize from JSON, else set as empty list
    if basket:
        basket = json.loads(basket)
    else:
        basket = []

    basket_quantity = sum(item['quantity'] for item in basket)

    return basket_quantity





@app.get("/customer/view-basket")
@x.require_role("customer")
@x.no_cache
def view_basket(role=None):
    user = session.get("account")
    user_pk = user.get("account_pk")
    basket = redis_client.get(user_pk)
    basket_quantity = get_basket_and_quantity(user_pk)

    if basket:
        # Ensure basket is a dictionary
        if isinstance(basket, (str, bytes, bytearray)):  # Decode JSON if necessary
            basket = json.loads(basket)
        elif not isinstance(basket, list):  # Handle unexpected types
            basket = []

        items = get_items_from_basket(basket)

        # Calculate total price
        total_price = sum(item['item_price'] * item['quantity'] for item in items)
        total_price = round(total_price, 2)  # Round to 2 decimal places

        return render_template('view_basket.html', items=items, user=user, total_price=total_price, role=role, basket_quantity=basket_quantity)
    
    total_price = 00.00  # Default to 0 if the basket is empty
    return render_template('view_basket.html', items=[], user=user, total_price=total_price, role=role, basket_quantity=basket_quantity)






@app.get("/add-item/<item_pk>")
def add_to_basket(item_pk):
    try:
        user = session.get("account")
        if not user:
            return redirect(url_for("view_login"))

        user_pk = user.get("account_pk")

        # Retrieve the basket from Redis
        basket = redis_client.get(user_pk)

        # If basket exists, decode it, else initialize an empty list
        if basket:
            if isinstance(basket, (str, bytes, bytearray)):  # Decode JSON if it's a string or bytes
                basket = json.loads(basket)
        else:
            basket = []

        # Check if the basket is a list of items (with 'item_pk' and 'quantity')
        if not isinstance(basket, list):
            basket = []

        # Retrieve the item details (including item price) using get_item_by_pk
        item_details = get_item_by_pk(item_pk)  # Use your existing function to get item details
        if isinstance(item_details, tuple):  # If an error occurred (based on your get_item_by_pk exception handling)
            return item_details[0]  # Return the error message
        
        item_price = item_details.get("item_price")  # Retrieve item price from the details

        # Convert Decimal to float to make it JSON serializable
        if isinstance(item_price, decimal.Decimal):
            item_price = float(item_price)

        # Look for the item in the basket
        item_found = False
        for item in basket:
            if item['item_pk'] == item_pk:
                item['quantity'] += 1  # Increment the quantity
                item_found = True
                break
        
        if not item_found:
            # If the item is not in the basket, add it with a quantity of 1 and the price
            basket.append({'item_pk': item_pk, 'quantity': 1, 'item_price': item_price})

        # Save the updated basket back to Redis
        redis_client.set(user_pk, json.dumps(basket))

        return redirect(url_for("view_basket"))
    
    except Exception as ex:
        ic(ex)
        return f"<template>There was an error adding the item to the basket</template>", 500






@app.get('/remove-item/<item_pk>')
@x.no_cache
def remove_from_basket(item_pk):
    user = session.get("account")
    if not user:
        return redirect(url_for("view_login"))

    user_pk = user.get("account_pk")

    # Retrieve the basket from Redis
    basket = redis_client.get(user_pk)

    if isinstance(basket, str):
        basket = json.loads(basket)

    try:
        # If the basket is a list, remove the item with the matching item_pk
        if isinstance(basket, list):
            basket = [item for item in basket if item.get('item_pk') != item_pk]

        # Save the updated basket back to Redis
        redis_client.set(user_pk, json.dumps(basket))

        app.logger.debug(f"Item removed: {item_pk}")

    except Exception as ex:
        app.logger.error(f"Error removing item: {ex}")
        return "<template>There was an error removing the item from the basket</template>", 500

    # Update the session with the modified basket
    session['basket'] = json.dumps(basket)
    session.modified = True
    app.logger.debug(f"Updated Basket: {session['basket']}")

    return redirect(url_for("view_basket"))






@app.get('/increase-quantity/<item_pk>')
@x.no_cache
def increase_quantity(item_pk):
    user = session.get("account")
    if not user:
        return redirect(url_for("view_login"))

    user_pk = user.get("account_pk")
    basket = redis_client.get(user_pk)

    if isinstance(basket, str):
        basket = json.loads(basket)

    # Check if the item exists in the basket, and increase its quantity
    for item in basket:
        if item['item_pk'] == item_pk:
            item['quantity'] += 1  # Increase quantity by 1
            break
    else:
        # If the item doesn't exist, add it with quantity 1
        basket.append({'item_pk': item_pk, 'quantity': 1})

    # Save updated basket
    redis_client.set(user_pk, json.dumps(basket))
    session['basket'] = json.dumps(basket)
    session.modified = True

    return redirect(url_for("view_basket"))


@app.get('/decrease-quantity/<item_pk>')
@x.no_cache
def decrease_quantity(item_pk):
    user = session.get("account")
    if not user:
        return redirect(url_for("view_login"))

    user_pk = user.get("account_pk")
    basket = redis_client.get(user_pk)

    if isinstance(basket, str):
        basket = json.loads(basket)

    # Find the item in the basket and decrease its quantity
    for item in basket:
        if item['item_pk'] == item_pk:
            if item['quantity'] > 1:
                item['quantity'] -= 1  # Decrease quantity by 1
            else:
                basket.remove(item)  # Remove item if quantity reaches 0
            break

    # Save updated basket
    redis_client.set(user_pk, json.dumps(basket))
    session['basket'] = json.dumps(basket)
    session.modified = True

    return redirect(url_for("view_basket"))




##############################
@app.get("/customer/restaurant/<restaurant_pk>")
@x.require_role("customer")
@x.no_cache
def view_single_restaurant(restaurant_pk, role=None):
    try:
        user = session.get("account")
        basket_quantity = get_basket_and_quantity(user.get('account_pk'))

        db, cursor = x.db()

        q = """
            SELECT 
                restaurant_pk, 
                restaurant_name, 
                restaurant_description,
                restaurant_image_name 
            FROM restaurants 
            WHERE restaurant_pk = %s 
            AND restaurant_deleted_at = 0"""
        
        cursor.execute(q,(restaurant_pk,))        
        restaurant = cursor.fetchone()

        if not restaurant:
            return render_template("error.html", message="Restaurant not found"), 404

        query = '''
            SELECT 
                i.item_pk, 
                i.item_title, 
                i.item_description, 
                i.item_price, 
                GROUP_CONCAT(ii.item_image_name) AS item_image_names
            FROM items i
            LEFT JOIN item_images ii ON i.item_pk = ii.item_image_item_fk
            WHERE i.item_deleted_at = 0 AND item_restaurant_fk = %s
            GROUP BY i.item_pk, i.item_title, i.item_description, i.item_price
        '''

        items = fetch_items(query, (restaurant_pk,))

        return render_template("view_single_restaurant.html", user=user, restaurant=restaurant, items=items, role=role, basket_quantity=basket_quantity)
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()









##############################
@app.get("/admin/users")
@x.no_cache
def view_all_users():
    try:
        user = session.get("account")
        if not 'admin' in user.get("roles"):
            return redirect(url_for("view_login"))
        
        db, cursor = x.db()
        q = 'SELECT account_pk, account_name, account_email, account_blocked_at, account_deleted_at, account_roles FROM accounts'
        cursor.execute(q)
        accounts = cursor.fetchall()

        return render_template('view_all_users.html', user=user, accounts=accounts)

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/admin/items")
@x.no_cache
def view_all_items_admin():
    try:
        user = session.get("account")
        if not 'admin' in user.get("roles"):
            return redirect(url_for("view_login"))
        db, cursor = x.db()
        q = '''
            SELECT 
                items.item_pk, 
                items.item_title, 
                items.item_price, 
                items.item_blocked_at, 
                items.item_deleted_at, 
                restaurants.restaurant_name
            FROM items
            LEFT JOIN restaurants ON items.item_restaurant_fk = restaurants.restaurant_pk
        '''
        cursor.execute(q)
        items = cursor.fetchall()

        return render_template('view_all_items_admin.html', user=user, items=items)

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
@app.get("/restaurant/create-item")
@x.no_cache
def view_create_item():
    user = session.get("account")
    if not 'restaurant' in user.get("roles"):
        return redirect(url_for("view_login"))
    return render_template("view_create_item.html", user=user, x=x)



##############################
@app.get("/restaurant/my-items")
@x.no_cache
def view_my_items():
    user = session.get("account")
    restaurant_pk = user.get("account_pk", "")
    if not 'restaurant' in user.get("roles"):
        return redirect(url_for("view_login"))

    items = get_items_for_restaurant(restaurant_pk)

    return render_template("view_my_items.html", user=user, x=x, items=items)

def get_items_for_restaurant(restaurant_pk):
    try:
        query = '''
            SELECT 
                i.item_pk, 
                i.item_title, 
                i.item_description, 
                i.item_price, 
                GROUP_CONCAT(ii.item_image_name) AS item_image_names
            FROM items i
            LEFT JOIN item_images ii ON i.item_pk = ii.item_image_item_fk
            WHERE i.item_deleted_at = 0 AND item_restaurant_fk = %s
            GROUP BY i.item_pk, i.item_title, i.item_description, i.item_price
        '''

        items = fetch_items(query, (restaurant_pk,))

        return items
    
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
@app.get("/restaurant/item/<item_pk>")
@x.no_cache
def view_edit_item(item_pk):
    user = session.get("account")
    if not 'restaurant' in user.get("roles"):
        return redirect(url_for("view_login"))

    item = get_item_for_edit(item_pk)
    if isinstance(item, tuple):
        return item

    return render_template("view_edit_item.html", item=item, user=user, x=x)


def get_item_for_edit(item_pk):
    try:
        db, cursor = x.db()

        q = """
            SELECT item_pk, item_title, item_description, item_price, item_restaurant_fk, item_images.item_image_name, item_images.item_image_pk
            FROM items
            LEFT JOIN item_images ON items.item_pk = item_images.item_image_item_fk
            WHERE item_pk = %s
            """
        cursor.execute(q, (item_pk,))
        rows = cursor.fetchall()

        if not rows:
            return "Item not found", 404

        item = rows[0]
        item['images'] = [{
            'item_image_pk': row['item_image_pk'], 
            'item_image_name': row['item_image_name']
        } for row in rows]

        return item
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template mix-target="#toast" mix-bottom>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return f"<template>Database error: {str(ex)} </template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
@app.get("/edit-profile")
def view_edit_profile():
    user = session.get("account")
    if not user: 
        return redirect(url_for("view_login"))
    user_pk = user.get("account_pk")
    if 'customer' not in user.get("roles") and 'partner' not in user.get("roles"):
        return redirect(url_for('view_login'))
    role = redis_client.get(f"user:{user_pk}:role")
    role = role if role else ""
    basket_quantity = get_basket_and_quantity(user.get('account_pk'))
    return render_template("view_edit_profile.html", user=user, x=x, role=role, basket_quantity=basket_quantity)



##############################
@app.get("/edit-restaurant-profile")
def view_edit_restaurant_profile():
    user = session.get("account")
    if not user: 
        return redirect(url_for("view_login"))
    if not 'restaurant' in user.get("roles"):
        return redirect(url_for("view_login"))
    return render_template("view_edit_restaurant_profile.html", user=user, x=x)



##############################
def get_search_items():
    try:
        user = session.get("account", "")
        search_text = request.args.get("search_field", "").strip()

        if not search_text or search_text == "":
            items = []
            restaurants = []
            return items, restaurants, search_text
        
        db, cursor = x.db()

        # Search query for items
        item_search_query = """
            SELECT 
            items.item_pk, 
            items.item_title, 
            items.item_description, 
            items.item_price, 
            GROUP_CONCAT(item_images.item_image_name) AS item_image_names
            FROM items
            LEFT JOIN item_images ON items.item_pk = item_images.item_image_item_fk
            WHERE items.item_deleted_at = 0 AND 
            (items.item_title LIKE %s OR items.item_description LIKE %s)
            GROUP BY items.item_pk
        """
        search_param = f"%{search_text}%"
        cursor.execute(item_search_query, (search_param, search_param))
        items = cursor.fetchall()

        for item in items:
            item['item_image_names'] = item['item_image_names'].split(',') if item['item_image_names'] else []


        # Search query for restaurants
        restaurant_search_query = """
            SELECT 
            restaurants.restaurant_pk, 
            restaurants.restaurant_name, 
            restaurants.restaurant_image_name
            FROM restaurants
            WHERE restaurants.restaurant_deleted_at = 0 AND
            (restaurants.restaurant_name LIKE %s)
        """
        cursor.execute(restaurant_search_query, (search_param,))
        restaurants = cursor.fetchall()

        return items, restaurants, search_text

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
@app.get("/search")
@x.require_role('customer')
@x.no_cache
def view_search_items(role=None):
    user = session.get("account", "")
    basket_quantity = get_basket_and_quantity(user.get('account_pk'))

    results = get_search_items()

    if isinstance(results, str):  # The result is an HTML response
        return results

    # Unpack results into items, restaurants, and search_text
    items, restaurants, search_text = results
    return render_template(
        "view_search_results.html",
        items=items,
        restaurants=restaurants,
        search_text=search_text,
        user=user,
        role=role,
        basket_quantity=basket_quantity
    )








@app.get("/page/<table_name>/<page_number>")
def get_more_items(table_name, page_number):
    try:
        # Validate and set defaults
        page_number = x.validate_page_number(page_number)
        db, cursor = x.db()

        # Define per-page limit and offset
        items_per_page = 6
        total_items_with_hanging = items_per_page + 1
        offset = (page_number - 1) * items_per_page

        # Table-specific query templates
        queries = {
            "items": '''
                SELECT 
                    i.item_pk, 
                    i.item_title, 
                    i.item_description, 
                    i.item_price, 
                    GROUP_CONCAT(ii.item_image_name) AS item_image_names
                FROM items i
                LEFT JOIN item_images ii ON i.item_pk = ii.item_image_item_fk
                WHERE i.item_deleted_at = 0
                GROUP BY i.item_pk, i.item_title, i.item_description, i.item_price
                LIMIT %s OFFSET %s
            ''',
            "restaurants": '''
                SELECT 
                    restaurant_pk, 
                    restaurant_name, 
                    restaurant_image_name 
                FROM restaurants r
                WHERE restaurant_deleted_at = 0
                GROUP BY r.restaurant_pk, r.restaurant_name
                LIMIT %s OFFSET %s
            '''
        }

        # Check if the table_name exists in queries
        if table_name not in queries:
            return "<template>Invalid table name</template>", 400

        # Execute the corresponding query
        query = queries[table_name]
        cursor.execute(query, (total_items_with_hanging, offset))
        results = cursor.fetchall()

        # Process the items based on the table
        if table_name == "items":
            for result in results:
                result['item_image_names'] = result['item_image_names'].split(',') if result['item_image_names'] else []

        # Server-side rendering of items
        html = ""

        for result in results[:items_per_page]:
            if table_name == "items":
                html_item = render_template("__item.html", item=result)
            elif table_name == "restaurants":
                html_item = render_template("__restaurant.html", restaurant=result)
            html += html_item

        db.commit()

        # Prepare the "More" button
        next_page = int(page_number) + 1
        new_button = render_template("___btn_more.html", next_page=next_page, table_name=table_name)
        if len(results) <= items_per_page:
            new_button = "<p>No more items</p>"


        return f"""
            <template mix-target="#{table_name}" mix-bottom>
                {html}
            </template>
            <template mix-target="#btn_next_page" mix-replace>
                {new_button}
            </template>
        """
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return ic(ex.message), ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
def get_lat_long_from_address(address):
    try:
        location = geolocator.geocode(address, timeout=10)  # Increase timeout
        if location:
            return location.latitude, location.longitude
        else:
            raise ValueError("Address not found")
    except Exception as ex:
        print(f"Error during geocoding: {ex}")
        return None, None


##############################
##############################
##############################

def _________POST_________(): pass

##############################
##############################
##############################

@app.route("/set_role/<role>", methods=["POST"])
def set_role(role):
    user_pk = session.get('account').get("account_pk") 
    redis_client.set(f"user:{user_pk}:role", role)  
    return redirect(f"/{role}")  


##############################
@app.post("/logout")
def logout():
    session.pop("account", None)
    return redirect(url_for("view_login"))


##############################
@app.post("/users")
@x.no_cache
def signup():
    try:
        selected_role = x.validate_user_role() 
        user_name = x.validate_account_name("user_name")
        user_last_name = x.validate_account_name("user_last_name")
        user_street = x.validate_account_address("user_street")
        user_postalcode = x.validate_account_postalcode("user_postalcode")
        user_city = x.validate_account_address("user_city")
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
            (user_pk, user_name, user_last_name, user_street, user_postalcode, user_city, user_email, 
            user_password, user_created_at, user_deleted_at, user_blocked_at, user_updated_at, 
            user_verified_at, user_verification_key)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        cursor.execute(q, (user_pk, user_name, user_last_name, user_street, user_postalcode, user_city, 
                            user_email, hashed_password, user_created_at, user_deleted_at, user_blocked_at, 
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
        restaurant_description = x.validate_restaurant_description()
        restaurant_street = x.validate_account_address("restaurant_street")
        restaurant_postalcode = x.validate_account_postalcode("restaurant_postalcode")
        restaurant_city = x.validate_account_address("restaurant_city")
        restaurant_email = x.validate_account_email("restaurant_email")
        restaurant_password = x.validate_account_password("restaurant_password")
        hashed_password = generate_password_hash(restaurant_password)
        
        valid_files = x.validate_item_image("restaurant_image_name")
        for file, file_name in valid_files:
            # Save the image to the server
            image_path = os.path.join(x.UPLOAD_RESTAURANT_FOLDER, file_name)
            file.save(image_path)
            restaurant_image_name = file_name

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
        
        address = f"{restaurant_street}, {restaurant_postalcode}, {restaurant_city}"
        latitude, longitude = get_lat_long_from_address(address)
        if latitude is None or longitude is None:
            toast = render_template("___toast.html", message="Invalid address. Could not geocode.")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
    
        q = '''
            INSERT INTO restaurants 
            (restaurant_pk, restaurant_name, restaurant_description, restaurant_street, restaurant_postalcode, restaurant_city, 
            restaurant_email, restaurant_password, restaurant_image_name, restaurant_latitude, 
            restaurant_longitude, restaurant_created_at, restaurant_deleted_at, restaurant_blocked_at, 
            restaurant_updated_at, restaurant_verified_at, restaurant_verification_key) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
        cursor.execute(q, (
            restaurant_pk, restaurant_name, restaurant_description, restaurant_street, restaurant_postalcode, restaurant_city, 
            restaurant_email, hashed_password, restaurant_image_name, latitude, longitude, restaurant_created_at, 
            restaurant_deleted_at, restaurant_blocked_at, restaurant_updated_at, restaurant_verified_at, 
            account_verification_key
        ))
        
        db.commit()

        x.send_verify_email(restaurant_email, account_verification_key)


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
            SELECT account_pk, account_name, restaurant_description, account_street, 
            account_postalcode, account_city, account_email,
            account_password, account_verified_at, account_roles,
            user_last_name, account_deleted_at
            FROM accounts
            LEFT JOIN users ON accounts.account_pk = users.user_pk
            LEFT JOIN restaurants ON accounts.account_pk = restaurants.restaurant_pk
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
            "account_description": rows[0].get("restaurant_description"),
            "account_street": rows[0]["account_street"],
            "account_postalcode": rows[0]["account_postalcode"],
            "account_city": rows[0]["account_city"],
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

        valid_files = x.validate_item_image("item_image_name") 
        
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




@app.post('/send-order-email')
def send_order_email():
    try:
        user = session.get("account")
        user_email = user.get("account_email")
        to_email = user_email  

        # Get the user's basket from Redis
        user_pk = user.get("account_pk")
        basket = redis_client.get(user_pk)  # Retrieve the basket from Redis or session
        
        # If the basket is not found, return an error
        if not basket:
            return jsonify({"error": "Basket is empty or not found."}), 400

        # Decode the basket if it's in string/byte format
        if isinstance(basket, (bytes, bytearray, str)):
            basket = json.loads(basket)

        # Now you have the basket, pass it to get_items_from_basket
        order = get_items_from_basket(basket)  # Pass the basket data here
        # If the order is empty, return an error
        if not order:
            return jsonify({"error": "No items found in the basket."}), 400
        
        # Calculate total price
        total_price = sum(item['item_price'] * item['quantity'] for item in order)

        # Send the order confirmation email
        order = x.format_order_details(order)
        x.send_order_confirmation_email(to_email, order, total_price)

        # Empty the basket after the email is sent 
        redis_client.delete(user_pk)

        return """<template mix-redirect="/order-confirmation"></template>""", 201
    
    except Exception as ex:
        # Handle error if any
        ic(f"Error: {ex}")
        return jsonify({"error": "An error occurred while sending the email."}), 500



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
        user_street = x.validate_account_address("user_street")
        user_postalcode = x.validate_account_postalcode("user_postalcode")
        user_city = x.validate_account_address("user_city")
        user_email = x.validate_account_email("user_email")
        user_updated_at = int(time.time())
        db, cursor = x.db()
        ic(user_email)
        
        # Fetch the current user info
        cursor.execute(
            """ SELECT user_name, user_last_name, user_street, user_postalcode, user_city, user_email, user_verified_at, user_verification_key 
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
            current_user["user_street"] == user_street and
            current_user["user_postalcode"] == user_postalcode and
            current_user["user_city"] == user_city and
            current_user["user_email"] == user_email ):
            
            toast = render_template("___toast.html", message="No changes made")
            return f"""<template mix-target="#toast">{toast}</template>"""
        
        user_verified_at = 0 if current_user["user_email"] != user_email else current_user["user_verified_at"]

        cursor.execute(
            """UPDATE users SET user_name = %s, user_last_name = %s, user_street = %s, 
            user_postalcode = %s, user_city = %s, user_email = %s, user_updated_at = %s, 
            user_verified_at = %s 
            WHERE user_pk = %s""",
            (user_name, user_last_name, user_street, user_postalcode, user_city, user_email, 
            user_updated_at, user_verified_at, user_pk))
        if cursor.rowcount != 1: 
            x.raise_custom_exception("cannot update user", 401)

        db.commit()

        session["account"].update({
            "account_name": user_name, 
            "account_last_name": user_last_name, 
            "account_street": user_street,
            "account_postalcode": user_postalcode,
            "account_city": user_city,
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
            restaurant_description = x.validate_restaurant_description()
            restaurant_street = x.validate_account_address("user_street")
            restaurant_postalcode = x.validate_account_postalcode("user_postalcode")
            restaurant_city = x.validate_account_address("user_city")
            restaurant_email = x.validate_account_email("user_email")
            restaurant_updated_at = int(time.time())

            db, cursor = x.db()

            cursor.execute(
                """ SELECT restaurant_name, restaurant_description, restaurant_street, restaurant_postalcode, 
                    restaurant_city, restaurant_email, restaurant_verified_at, restaurant_verification_key 
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
                current_user["restaurant_description"] == restaurant_description and
                current_user["restaurant_street"] == restaurant_street and
                current_user["restaurant_postalcode"] == restaurant_postalcode and
                current_user["restaurant_city"] == restaurant_city and
                current_user["restaurant_email"] == restaurant_email ):
                
                toast = render_template("___toast.html", message="No changes made")
                return f"""<template mix-target="#toast">{toast}</template>"""
            
            restaurant_verified_at = 0 if current_user["restaurant_email"] != restaurant_email else current_user["restaurant_verified_at"]

            cursor.execute(
                """UPDATE restaurants SET restaurant_name = %s, restaurant_description = %s, restaurant_street = %s, 
                    restaurant_postalcode = %s, restaurant_city = %s, restaurant_email = %s, restaurant_updated_at = %s, 
                    restaurant_verified_at = %s 
                WHERE restaurant_pk = %s""",
                (restaurant_name, restaurant_description, restaurant_street, restaurant_postalcode, restaurant_city, 
                restaurant_email, restaurant_updated_at, restaurant_verified_at, restaurant_pk))
            if cursor.rowcount != 1: 
                x.raise_custom_exception("cannot update user", 401)

            db.commit()

            session["account"].update({
                "account_name": restaurant_name, 
                "account_description": restaurant_description, 
                "account_street": restaurant_street,
                "account_postalcode": restaurant_postalcode,
                "account_city": restaurant_city,
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
    




@app.put("/restaurant/item/<item_pk>")
def item_update(item_pk):
    try:
        item_title = x.validate_account_name("item_title")
        item_description = x.validate_item_description()
        item_price = x.validate_item_price()
        item_image_name = request.files.getlist("item_image_name") 
        valid_files = [file for file in item_image_name if file and file.filename.strip()]
        item_updated_at = int(time.time())

        restaurant_pk = session.get("account").get("account_pk")

        db, cursor = x.db()

        q = """
            SELECT i.item_title, i.item_description, i.item_price, ii.item_image_name
            FROM items i
            LEFT JOIN item_images ii ON i.item_pk = ii.item_image_item_fk
            WHERE i.item_pk = %s AND i.item_restaurant_fk = %s
        """
        cursor.execute(q, (item_pk, restaurant_pk))
        rows = cursor.fetchall()

        current_item = {
            "item_title": rows[0]["item_title"] if rows else None,
            "item_description": rows[0]["item_description"] if rows else None,
            "item_price": str(rows[0]["item_price"]) if rows else None,
            "images": [row["item_image_name"] for row in rows if row["item_image_name"]]
        }

        ic(item_title, item_description, item_price)  # Log input data
        ic(current_item)  # Log current item data

        # Comparing current values with new ones, accounting for potential formatting issues
        if (
            current_item["item_title"].strip() == item_title.strip() and
            current_item["item_description"].strip() == item_description.strip() and
            str(current_item["item_price"]) == str(item_price).strip() and
            not valid_files):

            toast = render_template("___toast.html", message="No changes made")
            return f"""<template mix-target="#toast">{toast}</template>"""

        # Log the update query parameters
        ic(item_title, item_description, item_price, item_updated_at, item_pk, restaurant_pk)

        q = """
            UPDATE items
            SET item_title = %s, item_description = %s, item_price = %s, item_updated_at = %s
            WHERE item_pk = %s AND item_restaurant_fk = %s
        """
        cursor.execute(q, (item_title, item_description, item_price, item_updated_at, item_pk, restaurant_pk))
        ic(cursor.rowcount)  # Check how many rows were updated

        if valid_files:
            for file in valid_files:
                file_extension = os.path.splitext(file.filename)[1][1:]
                if file_extension not in x.ALLOWED_FILE_EXTENSIONS:
                    x.raise_custom_exception("File invalid type", 400)

                filename = f"{uuid.uuid4()}.{file_extension}"
                file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, filename))
                image_q = '''
                    INSERT INTO item_images (item_image_pk, item_image_item_fk, item_image_name)
                    VALUES (%s, %s, %s)
                '''
                cursor.execute(image_q, (str(uuid.uuid4()), item_pk, filename))

        db.commit()

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




@app.put("/block/<target_type>/<pk>")
def block_target(target_type, pk):
    try:
        # Validate UUID
        pk = x.validate_uuid4(pk)
        uuid4 = request.values.get("uuid4", "").strip()
        ic(uuid4)
        print(uuid4)
        blocked_at = int(time.time())

        db, cursor = x.db()

        # Fetch all relevant records
        queries = {
            "user": "SELECT user_pk, user_email FROM users WHERE user_pk = %s",
            "restaurant": "SELECT restaurant_pk, restaurant_email FROM restaurants WHERE restaurant_pk = %s",
            "item": "SELECT item_pk, item_restaurant_fk FROM items WHERE item_pk = %s"
        }

        if target_type not in queries:
            x.raise_custom_exception("Invalid target type", 400)

        cursor.execute(queries[target_type], (pk,))
        result = cursor.fetchone()  # Fetch single record

        if not result:
            x.raise_custom_exception(f"{target_type.capitalize()} not found", 404)

        # Determine the appropriate update query based on target_type
        if target_type == "user":
            email = result["user_email"]
            q = "UPDATE users SET user_blocked_at = %s WHERE user_pk = %s"

        elif target_type == "restaurant":
            email = result["restaurant_email"]
            q = "UPDATE restaurants SET restaurant_blocked_at = %s WHERE restaurant_pk = %s"

        elif target_type == "item":
            # For item, fetch the related restaurant email
            restaurant_fk = result["item_restaurant_fk"]
            cursor.execute("SELECT restaurant_email FROM restaurants WHERE restaurant_pk = %s", (restaurant_fk,))
            restaurant = cursor.fetchone()
            if not restaurant:
                x.raise_custom_exception("Restaurant not found for the item", 404)
            email = restaurant["restaurant_email"]  # Email related to the restaurant of the item
            q = "UPDATE items SET item_blocked_at = %s WHERE item_pk = %s"

        # Execute the update
        cursor.execute(q, (blocked_at, pk))
        db.commit()

        # Send email notifications
        if target_type in ["user", "restaurant"]:
            x.send_block_email(email)  # Send email for user or restaurant blocking
        if target_type == "item":
            x.send_item_block_email(email)  # Send email for item-related block

        # Render response templates
        unblock_html = render_template("___btn_unblock.html", pk=pk, target_type=target_type)
        toast = render_template("___toast.html", message=f"{target_type.capitalize()} blocked")

        return f"""
                <template mix-target="#block-{target_type}-{pk}" mix-replace>
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





@app.put("/unblock/<target_type>/<pk>")
def unblock_target(target_type, pk):
    try:
        pk = x.validate_uuid4(pk)

        db, cursor = x.db()

        if target_type == "user":
            q = '''
                UPDATE users 
                SET user_blocked_at = 0
                WHERE user_pk = %s
            '''
            cursor.execute(q, (pk,))
            if cursor.rowcount != 1:
                x.raise_custom_exception("Cannot unblock user", 400)


        elif target_type == "restaurant":
            q = '''
                UPDATE restaurants 
                SET restaurant_blocked_at = 0
                WHERE restaurant_pk = %s
            '''
            cursor.execute(q, (pk,))
            if cursor.rowcount != 1:
                x.raise_custom_exception("Cannot unblock restaurant", 400)

        elif target_type == "item":
            q = '''
                UPDATE items 
                SET item_blocked_at = 0
                WHERE item_pk = %s
            '''
            cursor.execute(q, (pk,))
            if cursor.rowcount != 1:
                x.raise_custom_exception("Cannot unblock item", 400)

        else:
            x.raise_custom_exception("Invalid target type", 400)

        db.commit()

        block_html = render_template("___btn_block.html", pk=pk, target_type=target_type)
        toast = render_template("___toast.html", message=f"{target_type.capitalize()} unblocked")

        return f"""
                <template mix-target="#unblock-{target_type}-{pk}" mix-replace>
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



##############################
@app.delete("/admin/delete/<target_type>/<pk>")
def delete_target(target_type, pk):
    try:
        # Check for user session and admin role
        account = session.get("account")
        if not account or "admin" not in account.get("roles", []):
            return redirect(url_for("view_login"))

        pk = x.validate_uuid4(pk)  # Validate the primary key (UUID)
        deleted_at = int(time.time())  # Get the current timestamp for deletion

        db, cursor = x.db()  # Open database connection

        # Queries for different target types
        queries = {
            "user": "SELECT user_pk, user_email FROM users WHERE user_pk = %s",
            "restaurant": "SELECT restaurant_pk, restaurant_email FROM restaurants WHERE restaurant_pk = %s",
            "item": "SELECT item_pk, item_restaurant_fk FROM items WHERE item_pk = %s"
        }

        # Ensure the target type is valid
        if target_type not in queries:
            x.raise_custom_exception("Invalid target type", 400)

        # Execute the query to check if the PK exists
        cursor.execute(queries[target_type], (pk,))
        result = cursor.fetchone()

        if not result:
            x.raise_custom_exception(f"{target_type.capitalize()} not found", 404)

        
        if target_type == "user":
            email = result["user_email"]
            q = "UPDATE users SET user_deleted_at = %s WHERE user_pk = %s"

        elif target_type == "restaurant":
            email = result["restaurant_email"]
            q = "UPDATE restaurants SET restaurant_deleted_at = %s WHERE restaurant_pk = %s"

        elif target_type == "item":
            restaurant_fk = result["item_restaurant_fk"]
            cursor.execute("SELECT restaurant_email FROM restaurants WHERE restaurant_pk = %s", (restaurant_fk,))
            restaurant = cursor.fetchone()
            if not restaurant:
                x.raise_custom_exception("Restaurant not found for the item", 404)
            email = restaurant["restaurant_email"]  
            q = "UPDATE items SET item_deleted_at = %s WHERE item_pk = %s"


        cursor.execute(q, (deleted_at, pk))
        db.commit()

        if target_type in ["user", "restaurant"]:
            x.send_delete_email(email)  
        if target_type == "item":
            x.send_item_delete_email(email)  


        deleted_at_html = render_template("___deleted_at.html", deleted_at=deleted_at)
        toast = render_template("___toast.html", message=f"{target_type.capitalize()} deleted")
        return f"""
                <template mix-target="#delete-{target_type}-{pk}" mix-replace>
                    {deleted_at_html}
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
@app.delete("/users/delete/<account_pk>")
def delete_user(account_pk):
    try:
        account_pk = x.validate_uuid4(account_pk)

        # Get the password from the X-Delete-Password header
        provided_password = request.headers.get("X-User-Confirmation")
        if not provided_password or provided_password.strip() == "":
            x.raise_custom_exception("Password missing", 404)
            

        account_deleted_at = int(time.time())

        db, cursor = x.db()

        q = "SELECT account_password, account_email FROM accounts WHERE account_pk = %s"
        cursor.execute(q, (account_pk,))
        result = cursor.fetchone()

        if not result:
            x.raise_custom_exception("User not found.", 404)

        stored_password_hash = result["account_password"]
        
        # Check if the provided password matches the stored password hash
        if not check_password_hash(stored_password_hash, provided_password):
            x.raise_custom_exception("Password incorrect", 404)

        account_roles = session.get("account").get("roles")

        # Check if roles contain either "customer" or "partner"
        if "customer" in account_roles or "partner" in account_roles:
            q_users = "UPDATE users SET user_deleted_at = %s WHERE user_pk = %s"
            cursor.execute(q_users, (account_deleted_at, account_pk))
        # Handle the restaurant role
        elif "restaurant" in account_roles:
            q_restaurants = "UPDATE restaurants SET restaurant_deleted_at = %s WHERE restaurant_pk = %s"
            cursor.execute(q_restaurants, (account_deleted_at, account_pk))
        else:
            x.raise_custom_exception("Invalid account role. No update performed.", 400)

        db.commit()

        session.pop("account", None)

        email = result["account_email"]
        x.send_delete_email(email)

        return """<template mix-redirect="/login"></template>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()




##############################
@app.delete("/restaurant/delete/item/<item_pk>")
def delete_item(item_pk):
    try:
        item_pk = x.validate_uuid4(item_pk)
        item_deleted_at = int(time.time())

        db, cursor = x.db()

        q = """
            SELECT item_pk
            FROM items
            WHERE item_pk = %s
        """
        cursor.execute(q, (item_pk,))
        row = cursor.fetchone()

        if row is None:
            x.raise_custom_exception("item not found", 404)

        # Delete the item from the database
        q = """
            UPDATE items
            SET item_deleted_at = %s
            WHERE item_pk = %s
        """
        cursor.execute(q, (item_deleted_at, item_pk))

        q = """
            SELECT item_image_name
            FROM item_images
            WHERE item_image_item_fk = %s
        """
        cursor.execute(q, (item_pk,))
        row = cursor.fetchone()
        if row is None:
            x.raise_custom_exception("images not found", 404)

        # Get the image filename
        image_filename = row["item_image_name"]

        # Remove the image file from the server's filesystem
        file_path = os.path.join(x.UPLOAD_ITEM_FOLDER, image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)


        db.commit()

        return f"""<template mix-redirect="/restaurant/my-items"></template>"""


    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template>{ex.message}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()





##############################
@app.delete("/restaurant/delete/item-image/<item_pk>/<item_image_pk>")
def delete_item_image(item_pk, item_image_pk):
    try:
        db, cursor = x.db()

        q = """
            SELECT item_image_name
            FROM item_images
            WHERE item_image_pk = %s AND item_image_item_fk = %s
        """
        cursor.execute(q, (item_image_pk, item_pk))
        row = cursor.fetchone()

        if row is None:
            return "<template>Image not found or unauthorized</template>", 404

        # Get the image filename
        image_filename = row["item_image_name"]

        # Remove the image file from the server's filesystem
        file_path = os.path.join(x.UPLOAD_ITEM_FOLDER, image_filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete the image record from the database
        delete_q = """
            DELETE FROM item_images
            WHERE item_image_pk = %s
        """
        cursor.execute(delete_q, (item_image_pk,))

        # Commit the changes
        db.commit()

        # Send a response indicating success
        toast = render_template("___toast.html", message="Image deleted successfully")
        return f"""<template mix-target="#toast">{toast}</template>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            return f"""<template>{ex.message}</template>""", ex.code        
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
        ic(cursor.rowcount) 
        
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
