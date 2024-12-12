import x
import uuid
import time
import random
from werkzeug.security import generate_password_hash
from faker import Faker
import json

fake = Faker()

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)


db, cursor = x.db()


def insert_restaurant(restaurant):       
    q = f"""
        INSERT INTO restaurants
        VALUES (%s, %s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s, %s, %s, %s, %s, %s, %s, %s)        
        """
    values = tuple(restaurant.values())
    cursor.execute(q, values)



try:
    ############################## 
    # Create 50 restaurants
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

    restaurant_password = hashed_password = generate_password_hash("password")
    for i in range(30):
        address = addresses[i]
        image_name = image_filenames[i]
        restaurant_name = restaurant_names[i]
        restaurant_pk = str(uuid.uuid4())
        restaurant_verified_at = random.choice([0,int(time.time())])
        address = random.choice(addresses)
        restaurant = {
            "restaurant_pk" : restaurant_pk,
            "restaurant_name" : restaurant_name,
            "restaurant_description" : fake.text(max_nb_chars=150),
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
            "restaurant_reset_password_key": None
        }
        insert_restaurant(restaurant)

    db.commit()

except Exception as ex:
    ic(ex)
    if "db" in locals(): db.rollback()

finally:
    if "cursor" in locals(): cursor.close()
    if "db" in locals(): db.close()
