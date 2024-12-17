import uuid
import time
from werkzeug.security import generate_password_hash
from faker import Faker
import random
import json
import x

fake = Faker()

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

# Assuming x.db() provides a valid database connection and cursor
db, cursor = x.db()

def insert_restaurant(restaurant):       
    q = f"""
        INSERT INTO restaurants
        (restaurant_pk, restaurant_name, restaurant_description, restaurant_street, restaurant_postalcode,
        restaurant_city, restaurant_email, restaurant_password, restaurant_image_name, restaurant_latitude,
        restaurant_longitude, restaurant_created_at, restaurant_deleted_at, restaurant_blocked_at,
        restaurant_updated_at, restaurant_verified_at, restaurant_verification_key, restaurant_reset_password_key)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = tuple(restaurant.values())
    cursor.execute(q, values)

try:
    ###########################
    # Step 1: Insert a Specific Restaurant for Login (admin use)
    restaurant_pk = str(uuid.uuid4())
    restaurant_email = "restaurant@company.com"  # This is the email you'll use for login
    restaurant_password = generate_password_hash("password")  # Password for the restaurant

    restaurant = {
        "restaurant_pk" : restaurant_pk,
        "restaurant_name" : "Test Restaurant",
        "restaurant_description" : fake.text(max_nb_chars=100),
        "restaurant_street": "Test Street 123",
        "restaurant_postalcode": 2200,
        "restaurant_city": "København",
        "restaurant_email" : restaurant_email,
        "restaurant_password" : restaurant_password,
        "restaurant_image_name": "/home/sofiehyllen/mysite/restaurant_images/restaurant_1.jpg",
        "restaurant_latitude": 55.686775,
        "restaurant_longitude": 12.545967,
        "restaurant_created_at" : int(time.time()),
        "restaurant_deleted_at" : 0,
        "restaurant_blocked_at" : 0,
        "restaurant_updated_at" : 0,
        "restaurant_verified_at" : int(time.time()),  # Ensure it's verified
        "restaurant_verification_key" : str(uuid.uuid4()),
        "restaurant_reset_password_key": 0
    }

    insert_restaurant(restaurant)  # Insert specific restaurant
    print(f"Restaurant {restaurant_email} inserted for login")

    ###########################
    # Step 2: Insert Multiple Random Restaurants for Data Seeding
    with open('addresses.json', 'r') as file:
        addresses = json.load(file)

    restaurant_names = [
        "The Hungry Fork", "Savory Bliss", "The Golden Plate", "Urban Bites", "Sunset Grill",
        "Bistro Boulevard", "Crave Kitchen", "The Rustic Table", "Coastal Catch", "Garden Feast",
        "Fire & Spice", "Moonlight Diner", "Harvest Haven", "Street Eats", "Fusion Delight",
        "Tasty Tavern", "The Cozy Spoon", "Bluebell Cafe", "Elegant Eats", "The Secret Garden",
        "La Petite Bistro", "Gourmet Gallery", "Riverfront Grill", "Flavors of the World",
        "The Spice Route", "Homestyle Haven", "Prime Cut Steakhouse", "Mediterranean Escape",
        "The Pasta Place", "Ocean's Bounty"
    ]
    image_folder = 'static/restaurant_images'
    image_filenames = [f"restaurant_{i}.jpg" for i in range(1, 31)]

    restaurant_password = generate_password_hash("password")
    for i in range(30):
        address = addresses[i]
        image_name = image_filenames[i]
        restaurant_name = restaurant_names[i]
        restaurant_verified_at = random.choice([0, int(time.time())])  # Randomly set verified or not
        restaurant_pk = str(uuid.uuid4())
        restaurant = {
            "restaurant_pk" : restaurant_pk,
            "restaurant_name" : restaurant_name,
            "restaurant_description" : fake.text(max_nb_chars=100),
            "restaurant_street": address["street"],
            "restaurant_postalcode": address["postalcode"],
            "restaurant_city": address["city"],
            "restaurant_email" : fake.unique.email(),
            "restaurant_password" : restaurant_password,
            "restaurant_image_name": image_name,
            "restaurant_latitude": address["latitude"],
            "restaurant_longitude": address["longitude"],
            "restaurant_created_at" : int(time.time()),
            "restaurant_deleted_at" : 0,
            "restaurant_blocked_at" : 0,
            "restaurant_updated_at" : 0,
            "restaurant_verified_at" : restaurant_verified_at,
            "restaurant_verification_key" : str(uuid.uuid4()),
            "restaurant_reset_password_key": 0
        }
        insert_restaurant(restaurant)

    db.commit()  # Commit the insertion of all data
    print("Data seeded successfully!")

except Exception as ex:
    ic(ex)
    if "db" in locals():
        db.rollback()

finally:
    if "cursor" in locals():
        cursor.close()
    if "db" in locals():
        db.close()
