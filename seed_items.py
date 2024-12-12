import x
import os
import uuid
import time
import random
from faker import Faker

fake = Faker()

db, cursor = x.db()


def insert_item(item):
    q = '''
        INSERT INTO items 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    values = tuple(item.values())
    cursor.execute(q, values)


def insert_item_image(item_image):
    query = '''
        INSERT INTO item_images 
        VALUES (%s, %s, %s)
    '''
    values = tuple(item_image.values())
    cursor.execute(query, values)

try:
    ############################## 
    # Create 8 items for each restaurants
    cursor.execute("SELECT restaurant_pk FROM restaurants")
    restaurants = cursor.fetchall()

    if not restaurants:
        raise ValueError("No restaurants found in the database.")

    # Define static values
    item_images_folder = 'static/item_images'
    available_images = os.listdir(item_images_folder)

    dishes = [
        "Margherita Pizza", "Spaghetti Carbonara", "Caesar Salad", "Grilled Chicken", "Beef Stroganoff",
        "Chicken Tikka Masala", "Vegetable Stir Fry", "Pad Thai", "Fish and Chips", "Sushi Platter",
        "Burrito Bowl", "Lobster Bisque", "Shrimp Scampi", "Ratatouille", "Eggplant Parmesan",
        "Shepherd's Pie", "Vegetarian Lasagna", "Chicken Alfredo", "Tuna Casserole", "Pulled Pork Sandwich",
        "BBQ Ribs", "Cheeseburger", "Miso Soup", "Tom Yum Soup", "Butter Chicken", "Greek Salad",
        "Tacos al Pastor", "Nachos Supreme", "Beef Wellington", "Chicken Cordon Bleu", "Pancakes",
        "Waffles", "Omelette", "French Toast", "Quiche Lorraine", "Mushroom Risotto", "Gnocchi",
        "Clam Chowder", "Stuffed Bell Peppers", "Roast Duck", "Beef Bourguignon", "Shakshuka",
        "Falafel Wrap", "Chicken Satay", "Spring Rolls", "Dim Sum", "Pho Noodle Soup", "Chili Con Carne",
        "Ceviche", "Paella", "Gazpacho", "Croque Monsieur", "Peking Duck", "Bibimbap", "Katsu Curry",
        "Teriyaki Salmon", "Korean Fried Chicken", "Bulgogi", "Paneer Butter Masala", "Dosa",
        "Biryani", "Vindaloo", "Tempura", "Jambalaya", "Gumbo", "Roast Lamb", "Grilled Shrimp",
        "Stuffed Mushrooms", "Chicken Caesar Wrap", "Meatloaf", "Cornbread", "Mac and Cheese",
        "Fettuccine Alfredo", "Vegetable Curry", "Samosas", "Chicken Wings", "Garlic Bread",
        "Pork Belly", "Crab Cakes", "Tuna Tartare", "Seafood Paella", "Duck à l'Orange",
        "Cauliflower Steak", "Spinach and Feta Pie", "Caprese Salad", "Antipasto Platter",
        "Hummus and Pita", "Kebabs", "Shawarma", "Lamb Chops", "Polenta", "Crispy Duck Salad",
        "Ramen Noodles", "Japanese Curry", "Hot Pot", "Quesadillas", "Empanadas", "Churros",
        "Tiramisu", "Crème Brûlée", "Baklava", "Cheesecake", "Brownies", "Apple Pie", "Pecan Pie",
        "Ice Cream Sundae", "Lemon Tart", "Chocolate Fondant", "Pavlova", "Sticky Toffee Pudding",
        "Mango Sticky Rice", "Fruit Salad", "Bread Pudding", "Cannoli", "Eclairs", "Macarons"
    ]

    dish_index = 0

    for restaurant in restaurants:
        restaurant_pk = restaurant["restaurant_pk"]

        for _ in range(8):  # 8 items per restaurant
            item_pk = str(uuid.uuid4())
            item_title = dishes[dish_index % len(dishes)]
            dish_index += 1
            item = {
                "item_pk": item_pk,
                "item_title": item_title,
                "item_description": fake.text(max_nb_chars=200),
                "item_price": round(random.uniform(5.0, 299.0), 2),
                "item_created_at": int(time.time()),
                "item_deleted_at": 0,
                "item_blocked_at": 0,
                "item_updated_at": 0,
                "item_restaurant_fk": restaurant_pk
            }

            insert_item(item)

            # Randomly pick 3 images for each item without duplicates
            chosen_images = random.sample(available_images, 3)
            for img_name in chosen_images:
                item_image = {
                    "item_image_pk": str(uuid.uuid4()),
                    "item_image_item_fk": item_pk,
                    "item_image_name": img_name
                }
                insert_item_image(item_image)

    db.commit()
    print("Items and images seeded successfully.")

except Exception as ex:
    print(f"An error occurred: {ex}")
    if "db" in locals():
        db.rollback()

finally:
    if "cursor" in locals():
        cursor.close()
    if "db" in locals():
        db.close()
