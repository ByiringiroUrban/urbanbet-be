import cloudinary
import cloudinary.uploader
from django.conf import settings


def configure_cloudinary() -> None:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )


def is_cloudinary_configured() -> bool:
    return bool(
        settings.CLOUDINARY_CLOUD_NAME
        and settings.CLOUDINARY_API_KEY
        and settings.CLOUDINARY_API_SECRET
    )


def upload_avatar_image(*, file_obj, user_id: int) -> str:
    configure_cloudinary()
    result = cloudinary.uploader.upload(
        file_obj,
        folder=settings.CLOUDINARY_AVATAR_FOLDER,
        public_id=f'user_{user_id}',
        overwrite=True,
        resource_type='image',
        invalidate=True,
    )
    return result['secure_url']
