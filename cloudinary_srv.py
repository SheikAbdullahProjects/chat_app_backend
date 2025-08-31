import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary.utils
import os
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)



def get_profile_picture_url(public_id: str):
    if not public_id:
        return None
    url, _ = cloudinary.utils.cloudinary_url(public_id, secure=True)
    return url

def upload_file(file, folder="user_profiles"):
    """
    Uploads a file to Cloudinary
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto"  # auto detects image, video, raw
        )
        return result
    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")


def delete_file(public_id: str):
    """
    Deletes a file from Cloudinary using its public_id
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result
    except Exception as e:
        raise Exception(f"Delete failed: {str(e)}")