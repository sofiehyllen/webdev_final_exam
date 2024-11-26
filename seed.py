import x
import uuid
import time
import random
from werkzeug.security import generate_password_hash
from faker import Faker

fake = Faker()

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)


db, cursor = x.db()


def insert_user(user):       
    q = f"""
        INSERT INTO users
        VALUES (%s, %s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)        
        """
    values = tuple(user.values())
    cursor.execute(q, values)


def insert_restaurant(restaurant):       
    q = f"""
        INSERT INTO restaurants
        VALUES (%s, %s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s ,%s)        
        """
    values = tuple(restaurant.values())
    cursor.execute(q, values)

try:
    ##############################
    #cursor.execute("DROP TABLE IF EXISTS items") # dependent table
    # cursor.execute("DROP TABLE IF EXISTS users")
    # cursor.execute("DROP TABLE IF EXISTS restaurants")
    # cursor.execute("DROP TABLE IF EXISTS users_roles") # dependent table
    # cursor.execute("DROP VIEW IF EXISTS accounts")


    ##############################
    # Create `users` table
    cursor.execute("""
    DROP TABLE IF EXISTS `users`;
    CREATE TABLE `users` (
        `user_pk` CHAR(36) NOT NULL,
        `user_name` VARCHAR(50) NOT NULL,
        `user_last_name` VARCHAR(50) NOT NULL,
        `user_email` VARCHAR(100) NOT NULL,
        `user_password` VARCHAR(255) NOT NULL,
        `user_created_at` INT UNSIGNED NOT NULL,
        `user_deleted_at` INT UNSIGNED NOT NULL,
        `user_blocked_at` INT UNSIGNED NOT NULL,
        `user_updated_at` INT UNSIGNED NOT NULL,
        `user_verified_at` INT UNSIGNED NOT NULL,
        `user_verification_key` CHAR(36) NOT NULL,
        `user_reset_password_key` CHAR(36) DEFAULT NULL,
        PRIMARY KEY (`user_pk`),
        UNIQUE KEY `user_email` (`user_email`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """)

    ##############################
  # Create `restaurants` table
    cursor.execute("""
    DROP TABLE IF EXISTS `restaurants`;
    CREATE TABLE `restaurants` (
        `restaurant_pk` CHAR(36) NOT NULL,
        `restaurant_name` VARCHAR(50) NOT NULL,
        `restaurant_email` VARCHAR(100) NOT NULL,
        `restaurant_password` VARCHAR(255) NOT NULL,
        `restaurant_created_at` INT UNSIGNED NOT NULL,
        `restaurant_deleted_at` INT UNSIGNED NOT NULL,
        `restaurant_blocked_at` INT UNSIGNED NOT NULL,
        `restaurant_updated_at` INT UNSIGNED NOT NULL,
        `restaurant_verified_at` INT UNSIGNED NOT NULL,
        `restaurant_verification_key` CHAR(36) NOT NULL,
        `restaurant_reset_password_key` CHAR(36) DEFAULT NULL,
        PRIMARY KEY (`restaurant_pk`),
        UNIQUE KEY `restaurant_email` (`restaurant_email`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """)
    ##############################
    # q = """
    #     CREATE TABLE items (
    #         item_pk CHAR(36),
    #         item_user_fk CHAR(36),
    #         item_title VARCHAR(50) NOT NULL,
    #         item_price DECIMAL(5,2) NOT NULL,
    #         item_image VARCHAR(50),
    #         PRIMARY KEY(item_pk)
    #     );
    #     """        
    # cursor.execute(q)
    # cursor.execute("ALTER TABLE items ADD FOREIGN KEY (item_user_fk) REFERENCES users(user_pk) ON DELETE CASCADE ON UPDATE RESTRICT") 


    ##############################
    # Create `roles` table
    cursor.execute("""
    DROP TABLE IF EXISTS `roles`;

    CREATE TABLE `roles` (
        `role_pk` CHAR(36) NOT NULL,
        `role_name` VARCHAR(20) NOT NULL,
        PRIMARY KEY (`role_pk`)
    ) 
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")


    ##############################    
    cursor.execute("""
    DROP TABLE IF EXISTS `users_roles`;

    CREATE TABLE `users_roles` (
        `user_role_user_fk` CHAR(36) NOT NULL,
        `user_role_role_fk` CHAR(36) NOT NULL,
        PRIMARY KEY (`user_role_user_fk`, `user_role_role_fk`),
        KEY `fk_users_roles_role` (`user_role_role_fk`),
        FOREIGN KEY (`user_role_role_fk`) REFERENCES `roles` (`role_pk`) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (`user_role_user_fk`) REFERENCES `users` (`user_pk`) ON DELETE CASCADE ON UPDATE CASCADE
    ) 
    ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;""")



    ##############################    
    # Create `accounts` view
    cursor.execute("""
    DROP VIEW IF EXISTS `accounts`;

    CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`%` SQL SECURITY DEFINER VIEW `accounts` AS 
    SELECT 
        `users`.`user_pk` AS `account_pk`, 
        `users`.`user_name` AS `account_name`, 
        `users`.`user_email` AS `account_email`, 
        `users`.`user_password` AS `account_password`, 
        `users`.`user_created_at` AS `account_created_at`, 
        `users`.`user_deleted_at` AS `account_deleted_at`, 
        `users`.`user_blocked_at` AS `account_blocked_at`, 
        `users`.`user_updated_at` AS `account_updated_at`, 
        `users`.`user_verified_at` AS `account_verified_at`, 
        `users`.`user_verification_key` AS `account_verification_key`, 
        GROUP_CONCAT(`roles`.`role_name` SEPARATOR ',') AS `account_role`, 
        'user' AS `entity_type` 
    FROM 
        `users`
    JOIN 
        `users_roles` ON `users`.`user_pk` = `users_roles`.`user_role_user_fk`
    JOIN 
        `roles` ON `users_roles`.`user_role_role_fk` = `roles`.`role_pk`
    GROUP BY 
        `users`.`user_pk`

    UNION ALL 

    SELECT 
        `restaurants`.`restaurant_pk` AS `account_pk`,
        `restaurants`.`restaurant_name` AS `account_name`,
        `restaurants`.`restaurant_email` AS `account_email`,
        `restaurants`.`restaurant_password` AS `account_password`,
        `restaurants`.`restaurant_created_at` AS `account_created_at`,
        `restaurants`.`restaurant_deleted_at` AS `account_deleted_at`,
        `restaurants`.`restaurant_blocked_at` AS `account_blocked_at`,
        `restaurants`.`restaurant_updated_at` AS `account_updated_at`,
        `restaurants`.`restaurant_verified_at` AS `account_verified_at`,
        `restaurants`.`restaurant_verification_key` AS `account_verification_key`,
        'restaurant' AS `account_role`,
        'restaurant' AS `entity_type`
    FROM 
        `restaurants`;
    """)


    ############################## 
    # Create roles
    cursor.execute("""
        INSERT INTO roles (role_pk, role_name)
        VALUES ("{x.ADMIN_ROLE_PK}", "admin"), ("{x.CUSTOMER_ROLE_PK}", "customer"), 
        ("{x.PARTNER_ROLE_PK}", "partner"), ("{x.RESTAURANT_ROLE_PK}", "restaurant")
        """)


    ############################## 
    # Create admin user
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "Sofie",
        "user_last_name" : "Hyllen",
        "user_email" : "admin@company.com",
        "user_password" : generate_password_hash("password"),
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4()),
        "user_reset_password_key": None
    }            
    insert_user(user)
    # Assign role to admin user
    cursor.execute("""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}", 
        "{x.ADMIN_ROLE_PK}")        
        """ )    




    ############################## 
    # Create customer
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "John",
        "user_last_name" : "Customer",
        "user_email" : "customer@company.com",
        "user_password" : generate_password_hash("password"),
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4()),
        "user_reset_password_key": None
    }
    insert_user(user)
    # Assign role to customer user
    cursor.execute("""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}", 
        "{x.CUSTOMER_ROLE_PK}")        
        """ )



    ############################## 
    # Create partner
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "John",
        "user_last_name" : "Partner",
        "user_email" : "partner@company.com",
        "user_password" : generate_password_hash("password"),
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4()),
        "user_reset_password_key": None
    }
    insert_user(user)
    # Assign role to partner user
    cursor.execute("""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}", 
        "{x.PARTNER_ROLE_PK}")        
        """ )



    ############################## 
    # Create restaurant
    restaurant_pk = str(uuid.uuid4())
    restaurant = {
        "restaurant_pk" : restaurant_pk,
        "restaurant_name" : "John's Restaurant",
        "restaurant_email" : "restaurant@fulldemo.com",
        "restaurant_password" : generate_password_hash("password"),
        "restaurant_created_at" : int(time.time()),
        "restaurant_deleted_at" : 0,
        "restaurant_blocked_at" : 0,
        "restaurant_updated_at" : 0,
        "restaurant_verified_at" : int(time.time()),
        "restaurant_verification_key" : str(uuid.uuid4())
    }
    insert_restaurant(restaurant)
    # Assign role to restaurant 
    cursor.execute("""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}", 
        "{x.RESTAURANT_ROLE_PK}")        
        """  )


    ############################## 
    # Create 50 customer
    domains = ["example.com", "testsite.org", "mydomain.net", "website.co", "fakemail.io", "gmail.com", "hotmail.com"]
    user_password = hashed_password = generate_password_hash("password")
    for _ in range(50):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user = {
            "user_pk" : user_pk,
            "user_name" : fake.first_name(),
            "user_last_name" : fake.last_name(),
            "user_email" : fake.unique.user_name() + "@" + random.choice(domains),
            "user_password" : user_password,
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : str(uuid.uuid4()),
            "user_reset_password_key": None
        }

        insert_user(user)
        cursor.execute("""INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)""", (user_pk, x.CUSTOMER_ROLE_PK))


    ############################## 
    # Create 50 partners
    user_password = hashed_password = generate_password_hash("password")
    for _ in range(50):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user = {
            "user_pk" : user_pk,
            "user_name" : fake.first_name(),
            "user_last_name" : fake.last_name(),
            "user_email" : fake.unique.email(),
            "user_password" : user_password,
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : str(uuid.uuid4()),
            "user_reset_password_key": None
        }

        insert_user(user)

        cursor.execute("""
        INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)
        """, (user_pk, x.PARTNER_ROLE_PK))



    ############################## 
    # Create 50 restaurants
    restaurant_password = hashed_password = generate_password_hash("password")
    for _ in range(50):
        restaurant_pk = str(uuid.uuid4())
        restaurant_verified_at = random.choice([0,int(time.time())])
        restaurant = {
            "restaurant_pk" : restaurant_pk,
            "restaurant_name" : f"Restaurant {fake.first_name()}",
            "restaurant_email" : fake.unique.email(),
            "restaurant_password" : restaurant_password,
            "restaurant_created_at" : int(time.time()),
            "restaurant_deleted_at" : 0,
            "restaurant_blocked_at" : 0,
            "restaurant_updated_at" : 0,
            "restaurant_verified_at" : restaurant_verified_at,
            "restaurant_verification_key" : str(uuid.uuid4()),
            "restaurant_reset_password_key": None

        }
        insert_restaurant(restaurant)

        # cursor.execute("""
        # INSERT INTO users_roles (
        #     user_role_user_fk,
        #     user_role_role_fk)
        #     VALUES (%s, %s)
        # """, (user_pk, x.RESTAURANT_ROLE_PK))

        # dishes = ["Spaghetti Carbonara","Chicken Alfredo","Beef Wellington","Sushi","Pizza Margherita","Tacos","Caesar Salad","Fish and Chips","Pad Thai","Dim Sum","Croissant","Ramen","Lasagna","Burrito","Chicken Parmesan","Tom Yum Soup","Shawarma","Paella","Hamburger","Pho","Chicken Tikka Masala","Moussaka","Goulash","Bangers and Mash","Peking Duck","Falafel","Ceviche","Chili Con Carne","Ratatouille","Beef Stroganoff","Fajitas","Samosas","Lobster Roll","Arancini","Tiramisu","Beef Empanadas","Poutine","Biryani","Hummus","Schnitzel","Meatloaf","Quiche","Paella Valenciana","Clam Chowder","Sweet and Sour Pork","Enchiladas","Crepes","Masala Dosa","Gnocchi","Jambalaya","Pork Ribs","Tandoori Chicken","Nasi Goreng","Kimchi","Roti","Lamb Tagine","Risotto","Croque Monsieur","Beef Burritos","Baked Ziti","Yakitori","Fettuccine Alfredo","Peking Duck Pancakes","Empanadas","Ahi Poke","Cacciatore","Pappardelle","Cannelloni","Empanadas de Pollo","Gado-Gado","Carne Asada","Chicken Katsu","Falafel Wrap","Maki Rolls","Stuffed Bell Peppers","Souvlaki","Bibimbap","Tofu Stir Fry","Chilaquiles","Mango Sticky Rice","Ragu","Beef Brisket","Tortilla Española","Panzanella","Chicken Shawarma","Pesto Pasta","Bulgogi","Maki Sushi","Cordon Bleu","Blini with Caviar","Clafoutis","Salmon Teriyaki","Shrimp Scampi","Frittata","Chateaubriand","Crab Cakes","Chicken Fried Rice","Hot Pot","Mole Poblano","Tofu Scramble"]
        # for _ in range(random.randint(5,50)):
        #     dish_id = random.randint(1, 100)
        #     cursor.execute("""
        #     INSERT INTO items (
        #         item_pk, item_user_fk, item_title, item_price, item_image)
        #         VALUES (%s, %s, %s, %s, %s)
        #     """, (str(uuid.uuid4()), user_pk, random.choice(dishes), round(random.uniform(50, 999), 2)), f"dish_{dish_id}.jpg")                




    db.commit()

except Exception as ex:
    ic(ex)
    if "db" in locals(): db.rollback()

finally:
    if "cursor" in locals(): cursor.close()
    if "db" in locals(): db.close()


