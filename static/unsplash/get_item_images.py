import requests
from dotenv import load_dotenv
import os

load_dotenv()

# Unsplash search endpoint for photos
url = "https://api.unsplash.com/search/photos"
headers = {
    "Authorization": f"Client-ID {os.getenv('UNSPLASH_ACCESS_KEY')}"
}

# Search parameters
search_params = {
    "query": "food dishes",  # Keywords to find profile-style images
    "per_page": 30,                # Max images per request
    "page": 1                      # Start on the first page
}

# Folder to save images
save_folder = "static/item_images"
os.makedirs(save_folder, exist_ok=True)

def download_image(image_url, save_path):
    """Downloads an image from a URL and saves it locally."""
    img_data = requests.get(image_url).content
    with open(save_path, "wb") as handler:
        handler.write(img_data)
    print(f"Downloaded {save_path}")

# Function to get profile images
def get_item_images(total_images=100):
    images_downloaded = 0
    page = 1

    while images_downloaded < total_images:
        search_params["page"] = page
        response = requests.get(url, headers=headers, params=search_params)
        if response.status_code == 200:
            results = response.json()["results"]
            if not results:
                print("No more images found.")
                break

            for img in results:
                if images_downloaded >= total_images:
                    break

                img_url = img["urls"]["regular"]
                img_name = f"item_{images_downloaded + 1}.jpg"
                save_path = os.path.join(save_folder, img_name)
                download_image(img_url, save_path)
                images_downloaded += 1

            page += 1
        else:
            print(f"Failed to fetch images: {response.status_code}")
            break

get_item_images(240)
