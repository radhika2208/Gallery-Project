"""
This file defines dictionaries containing validation error messages and success messages
for the Image and Video Gallery .
The VALIDATION dictionary contains error messages for form validation,
while the SUCCESS_MESSAGES dictionary contains success messages for various operations in the app.
"""
VALIDATION = {
    'gallery_name': {
        "blank": "Gallery name can not be blank",
        "required": "Please provide a gallery name",
        "exists": "Gallery with this name already exists"
    },
    'image': {
        "required": "Please provide a image",
        "max_size": "Make sure the image size is less than 2 Mb",
        "no_image": "No images found"
    },
    'image_gallery_id': {
        "required": "Please provide a image gallery id",
    },
    'image_gallery_set': {
        'no_album': 'No album found',
        'max_limit': 'Cannot upload more than 10 images.',
        'available_slots': 'Make sure you have enough space in the gallery',
    },
    'video_gallery_name': {
        "blank": "Video Gallery name can not be blank",
        "required": "Please provide a name to video gallery",
        "exists": "Video Gallery with this name already exists",
        "exists_while_updating": "A video gallery with this name already exists for the current user."
    },

    'video': {
        "required": "Please provide a video",
        "format": "Only mp4 files are allowed.",
        "max_size": "File size should be less than 50MB."
    },

    'video_gallery_id': {
        "required": "Please provide a video gallery id",
    },
    'video_gallery_set': {
        'no_album': 'No album found',
        'max_limit': 'Cannot upload more than 10 videos.',
    }
}
SUCCESS_MESSAGES = {
    "IMAGE_GALLERY": {
        "CREATED_SUCCESSFULLY": "Gallery created successfully",
        "UPDATED_SUCCESSFULLY": "Gallery updated successfully",
        "DELETED_SUCCESSFULLY": "Gallery deleted successfully",
    },
    "IMAGE": {
        "CREATED_SUCCESSFULLY": "Image uploaded successfully",
        "DELETED_SUCCESSFULLY": "Image deleted successfully",
    },
"VIDEO_GALLERY": {
        "CREATED_SUCCESSFULLY": "Video Gallery created successfully",
        "UPDATED_SUCCESSFULLY": "Video Gallery updated successfully",
        "DELETED_SUCCESSFULLY": "Video Gallery deleted successfully",
    },
    "VIDEO": {
        "CREATED_SUCCESSFULLY": "Video uploaded successfully",
        "DELETED_SUCCESSFULLY": "Video deleted successfully",
    }
}
ERROR_MESSAGES = {
    'IMAGE': {
        'NO_IMAGE': "This Gallery is empty"
    }
}
