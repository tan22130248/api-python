import cloudinary
import os

def init_cloudinary():
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME") or "dlyhvdonu",
        api_key=os.getenv("CLOUDINARY_API_KEY") or "358137225132925",
        api_secret=os.getenv("CLOUDINARY_API_SECRET") or "bSvXNjEDBhwnVsvS5FEFrRg7s18"
    )