"""
This file contains different serializers for Image, ImageGallery, Video , VideoGallery objects.
They handle serialization and deserialization of these objects
"""
import os

from django.shortcuts import get_object_or_404
from rest_framework import serializers

from gallery.constants import MAX_LENGTH, MIN_LENGTH, IMAGE_GALLERY_PATH, VIDEO_GALLERY_PATH, MAX_LIMIT, \
    MAX_SIZE_IMAGE, MAX_SIZE_VIDEO, VIDEO_FORMAT
from gallery.messages import VALIDATION
from gallery.models import ImageGallery, Image, VideoGallery, Video
from gallery.utils import generate_unique_image, generate_unique_video_filename


class ImageSerializer(serializers.ModelSerializer):
    """
     Serializer for the Image model with two required fields:
     'gallery' and 'image_gallery_id'.
     The 'error_messages' argument is used to specify custom error messages
     in case of validation errors.
    """
    image = serializers.SerializerMethodField()
    image_gallery_id = serializers.IntegerField(
        required=True, error_messages=VALIDATION['image_gallery_id'])

    def get_image(self, obj):
        """
        Returns the absolute URL of an image associated with the given object.
        :param obj:Image object
        :return: The absolute URL of the image
        """
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url)
        return None

    # pylint: disable=too-few-public-methods
    class Meta:
        """
        Use the Meta class to specify the model and fields
        that the ImageSerializer should work with
        """
        model = Image
        fields = ['id', 'image', 'image_gallery_id', 'created_at', 'updated_at']


class ImageCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for the Image model creating a new Image instance with two required fields:
    'gallery' and 'image_gallery_id'.
    The 'error_messages' argument is used to specify custom error messages
    in case of validation errors.
    """
    image = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        error_messages=VALIDATION['image']
    )
    image_gallery_id = serializers.IntegerField(
        required=True, error_messages=VALIDATION['image_gallery_id'])

    def validate(self, attrs):
        """
        Validation to check user cannot
        upload more than 10 images in a single gallery
        :param attrs: image_gallery_id
        :return: if valid return attrs ,else return Validation error
        """
        image_gallery_id = attrs.get('image_gallery_id')
        user = self.context['request'].user
        if image_gallery_id:
            gallery = get_object_or_404(ImageGallery, id=image_gallery_id, user=user)
            images = attrs.get('image', [])
            if len(images) + gallery.image_gallery_set.count() > MAX_LIMIT['max_limit']:
                raise serializers.ValidationError(VALIDATION['image_gallery_set']['max_limit'])
        return attrs

    @staticmethod
    def validate_image(value):
        """
        This function validates the size of the uploaded gallery and
        raises a validation error if it exceeds the maximum size limit specified in MAX_SIZE
        :param value: gallery
        :return: if valid return value ,else return Validation error
        """
        for image in value:
            if image.size > MAX_SIZE_IMAGE['max_size']:
                raise serializers.ValidationError(VALIDATION['image']['max_size'])
            return value

    def create(self, validated_data):
        """
        Override the create method to add custom behavior
        when creating a new Image instance
        It generates a unique filename for the uploaded image
        """
        user = self.context['request'].user
        image_gallery = get_object_or_404(
            ImageGallery, id=validated_data['image_gallery_id'], user=user
        )
        images = []

        for image in validated_data['image']:
            image_name = generate_unique_image(user, image_gallery, validated_data)
            image.name = str(image_name)
            image_instance = Image(
                image_gallery=image_gallery,
                image=image,
            )
            images.append(image_instance)
        Image.objects.bulk_create(images)
        return images

    # pylint: disable=too-few-public-methods
    class Meta:
        """
        Use the Meta class to specify the model and fields
        that the ImageCreateSerializer should work with
        """
        model = Image
        fields = ['id', 'image', 'image_gallery_id', 'created_at', 'updated_at']


class ImageGallerySerializer(serializers.ModelSerializer):
    """
    Serializer for the ImageGallery model with two required fields:
    'image_gallery_set' and 'gallery_name'.
    The 'error_messages' argument is used to specify custom error messages
    in case of validation errors.
    """
    image_gallery_set = ImageSerializer(many=True, read_only=True)
    gallery_name = serializers.CharField(
        min_length=MIN_LENGTH['gallery_name'], max_length=MAX_LENGTH['gallery_name'],
        required=True, error_messages=VALIDATION['gallery_name'])

    # pylint: disable=too-few-public-methods
    class Meta:
        """
        Use the Meta class to specify the model and fields
        that the ImageGallerySerializer should work with
        """
        model = ImageGallery
        fields = ['id', 'gallery_name', 'image_gallery_set', 'created_at', 'updated_at']


class ImageGalleryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for the ImageGallery model creating a new ImageGallery instance with
    one required field:'gallery_name'.
    The 'error_messages' argument is used to specify custom error messages
    in case of validation errors.
    """
    gallery_name = serializers.CharField(
        min_length=MIN_LENGTH['gallery_name'], max_length=MAX_LENGTH['gallery_name'],
        required=True, error_messages=VALIDATION['gallery_name'])

    def validate_gallery_name(self, value):
        """
        Validation to check if gallery already exists
        :param value: gallery_name
        :return: if valid return value, else return Validation error
        """
        user = self.context['request'].user
        if ImageGallery.objects.filter(user=user, gallery_name=value).exists():
            raise serializers.ValidationError(VALIDATION['gallery_name']['exists'])

        return value

    def create(self, validated_data):
        """
        Override the create method to add custom behavior
        when creating a new ImageGallery instance
        It then generates a path for the new gallery using a string format method,
        and creates the directory specified in the path using
        'os.makedirs' with the 'exist_ok' parameter set to True.
        """
        user = self.context['request'].user
        image_gallery = ImageGallery.objects.create(user=user, **validated_data)
        path = IMAGE_GALLERY_PATH.format(
            username=user.username, gallery_name=image_gallery.gallery_name
        )
        os.makedirs(path, exist_ok=False)
        return image_gallery

    # pylint: disable=too-few-public-methods
    class Meta:
        """
        Use the Meta class to specify the model and fields
        that the ImageGalleryCreateSerializer should work with
        """
        model = ImageGallery
        fields = ['id', 'gallery_name', 'created_at', 'updated_at']


class ImageGalleryUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for the ImageGallery model updating an existing ImageGallery instance
    with one required field: 'gallery_name'.
    The 'error_messages' argument is used to specify custom error messages
    in case of validation errors.
    """
    gallery_name = serializers.CharField(min_length=MIN_LENGTH['gallery_name'],
                                         max_length=MAX_LENGTH['gallery_name'],
                                         required=True, error_messages=VALIDATION['gallery_name'])

    def validate_gallery_name(self, value):
        """
        Validation to check if gallery already exists
        :param value: gallery_name
        :return: if valid return value, else return Validation error
        """
        user = self.context['request'].user
        if ImageGallery.objects.filter(user=user, gallery_name=value).exists():
            raise serializers.ValidationError(VALIDATION['gallery_name']['exists'])

        return value

    def update(self, instance, validated_data):
        """
        Override the update method to add custom behavior
        when updating an existing ImageGallery instance
        The method then generates old and new paths for the gallery using a
        string format method,and renames the old directory to the new directory using 'os.rename'.
        """
        user = self.context['request'].user
        ImageGallery.objects.filter(id=instance.id).update(**validated_data)
        old_path = IMAGE_GALLERY_PATH.format(
            username=user.username, gallery_name=instance.gallery_name
        )
        new_path = IMAGE_GALLERY_PATH.format(
            username=user.username, gallery_name=validated_data['gallery_name']
        )
        os.rename(old_path, new_path)
        updated_instance = ImageGallery.objects.get(id=instance.id)
        return updated_instance

    # pylint: disable=too-few-public-methods
    class Meta:
        """
        Use the Meta class to specify the model and fields
        that the ImageGalleryUpdateSerializer should work with
        """
        model = ImageGallery
        fields = ['id', 'gallery_name', 'created_at', 'updated_at']


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer VideoSerializer to list videos.
    """
    video = serializers.SerializerMethodField()
    video_gallery_id = serializers.IntegerField(
        required=True, error_messages=VALIDATION['video_gallery_id'])
    gallery_name = serializers.SerializerMethodField()

    def get_video(self, obj):
        """
        Returns the absolute URL of a video associated with the given object.
        :param obj:Video object
        :return: The absolute URL of the video
        """
        if obj.video:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.video.url)
        return None

    @staticmethod
    def get_gallery_name(obj):
        """
        Serializer method to return the gallery name
        of the related VideoGallery instance.
        """
        return obj.video_gallery.gallery_name

    class Meta:
        """
        class Meta to specify the model and fields
        that the serializer should work with
        """
        model = Video
        fields = ['id', 'video', 'video_gallery_id', 'gallery_name', 'created_at', 'updated_at']


class VideoGallerySerializer(serializers.ModelSerializer):
    """
     Serializer VideoGallerySerializer list a video gallery.
     """
    video_gallery_set = VideoSerializer(many=True, read_only=True)
    gallery_name = serializers.CharField(
        min_length=MIN_LENGTH['gallery_name'], max_length=MAX_LENGTH['gallery_name'],
        required=True, error_messages=VALIDATION['gallery_name'])

    class Meta:
        """
        class Meta to specify the model and fields
        that the serializer should work with
        """
        model = VideoGallery
        fields = ['id', 'gallery_name', 'video_gallery_set', 'created_at', 'updated_at']


class VideoGalleryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer VideoGalleryCreateSerializer creates a new video gallery.
    """
    gallery_name = serializers.CharField(
        min_length=MIN_LENGTH['gallery_name'], max_length=MAX_LENGTH['gallery_name'],
        required=True, error_messages=VALIDATION['gallery_name'])

    @staticmethod
    def validate_gallery_name(value):
        """
        Validator function to check if a video gallery with the given name already exists
        """
        if VideoGallery.objects.filter(gallery_name=value).exists():
            raise serializers.ValidationError(VALIDATION['video_gallery_name']['exists'])
        return value

    def create(self, validated_data):
        """
        Override the create method to add custom behavior
        when creating a new VideoGallery instance
        """
        user = self.context['request'].user
        video_gallery = VideoGallery.objects.create(user=user, **validated_data)
        path = VIDEO_GALLERY_PATH.format(
            username=user.username, gallery_name=video_gallery.gallery_name
        )
        os.makedirs(path, exist_ok=False)
        return video_gallery

    class Meta:
        """
        class Meta to specify the model and fields
        that the serializer should work with
        """
        model = VideoGallery
        fields = ['id', 'gallery_name', 'created_at', 'updated_at']


class VideoGalleryUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer VideoGalleryUpdateSerializer
    updates an existing Video Gallery .
    """
    gallery_name = serializers.CharField(
        min_length=MIN_LENGTH['gallery_name'],
        max_length=MAX_LENGTH['gallery_name'],
        required=True,
        error_messages=VALIDATION['gallery_name'])

    def validate_gallery_name(self, value):
        """
               Validation to check if gallery already exists
               :param value: gallery_name
               :return: if valid return value, else return Validation error
               """
        user = self.context['request'].user
        if VideoGallery.objects.filter(user=user, gallery_name=value).exists():
            raise serializers.ValidationError(VALIDATION['video_gallery_name']['exists_while_updating'])
        return value

    def update(self, instance, validated_data):
        """
        Override the update method to add custom behavior
        when updating an existing VideoGallery instance
        """
        user = self.context['request'].user
        VideoGallery.objects.filter(id=instance.id).update(**validated_data)
        old_path = VIDEO_GALLERY_PATH.format(
            username=user.username, gallery_name=instance.gallery_name
        )
        new_path = VIDEO_GALLERY_PATH.format(
            username=user.username, gallery_name=validated_data['gallery_name']
        )
        os.rename(old_path, new_path)
        updated_instance = VideoGallery.objects.get(id=instance.id)
        return updated_instance

    class Meta:
        """
        class Meta to specify the model and fields
        that the serializer should work with
        """
        model = VideoGallery
        fields = ['id', 'gallery_name', 'created_at', 'updated_at']


class VideoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for the Video model creating a new Video instance with two required fields:
    'gallery' and 'video_gallery_id'.
    The 'error_messages' argument is used to specify custom error messages
    in case of validation errors.
    """
    video = serializers.ListField(
        child=serializers.FileField(),
        required=True,
        error_messages=VALIDATION['video']
    )
    video_gallery_id = serializers.IntegerField(
        required=True, error_messages=VALIDATION['video_gallery_id'])

    @staticmethod
    def validate_video(value):
        """
        Custom validation function to ensure that the video file format is mp4
        and the size of each file is less than 50MB
        """
        for file in value:
            filename, ext = os.path.splitext(file.name)
            if ext.lower() != VIDEO_FORMAT:
                raise serializers.ValidationError(VALIDATION['video']['format'])
            if file.size > MAX_SIZE_VIDEO['max_size']:
                raise serializers.ValidationError(VALIDATION['video']['max_size'])
        return value

    def validate(self, attrs):
        """
        Validation to check user cannot
        upload more than 10 videos in a single gallery
        :param attrs: video_gallery_id
        :return: if valid return attrs ,else return Validation error
        """
        video_gallery_id = attrs.get('video_gallery_id')
        user = self.context['request'].user
        if video_gallery_id:
            gallery = get_object_or_404(VideoGallery, id=video_gallery_id, user=user)
            videos = attrs.get('video', [])
            if len(videos) + gallery.video_gallery_set.count() > MAX_LIMIT['max_limit']:
                raise serializers.ValidationError(VALIDATION['video_gallery_set']['max_limit'])
        return attrs

    def create(self, validated_data):
        """
        Override the create method to add custom behavior
        when creating a new Image instance
        It generates a unique filename for the uploaded image
        """
        user = self.context['request'].user
        video_gallery = get_object_or_404(
            VideoGallery, id=validated_data['video_gallery_id'], user=user
        )
        videos = []
        for video in validated_data['video']:
            video_name = generate_unique_video_filename(user, video_gallery, validated_data)
            video.name = str(video_name)
            video_instance = Video(
                video_gallery=video_gallery,
                video=video,
            )
            videos.append(video_instance)
        Video.objects.bulk_create(videos)
        return videos

    class Meta:
        """
        Use the Meta class to specify the model and fields
        that the VideoCreateSerializer should work with
        """
        model = Video
        fields = ['id', 'video', 'video_gallery_id', 'created_at', 'updated_at']
