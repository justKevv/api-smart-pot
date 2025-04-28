import cloudinary
import cloudinary.uploader
import cloudinary.utils
import os

class CloudinaryHandler:
    def __init__(self):
        cloudinary.config(
            cloud_name='dcj08h5jm',
            api_key='649636957145547',
            api_secret=os.environ.get('CLOUDINARY_API'),
            secure=True
        )

    def upload_image(self, img_bytes_io, public_id):
        cloudinary.uploader.upload(
            img_bytes_io,
            public_id=public_id,
            overwrite=True,
            invalidate=True
        )

        url, options = cloudinary.utils.cloudinary_url(
            public_id,
            secure=True,
            version=None
        )
        return url
