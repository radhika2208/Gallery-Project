"""
This file contains different ViewSets for 'Image','ImageGallery','Video','VideoGallery'
"""
import os
import shutil

from rest_framework import viewsets, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from gallery.constants import MEDIA_URL, IMAGE_PATH_TEMPLATE, \
    IMAGE_GALLERY_PATH, VIDEO_PATH_TEMPLATE, VIDEO_GALLERY_PATH
from gallery.messages import SUCCESS_MESSAGES, VALIDATION
from gallery.models import ImageGallery, Image, VideoGallery, Video
from gallery.serializers import ImageGallerySerializer, ImageGalleryCreateSerializer, \
    ImageGalleryUpdateSerializer, ImageCreateSerializer, ImageSerializer, \
    VideoGallerySerializer, VideoGalleryCreateSerializer, VideoGalleryUpdateSerializer, \
    VideoCreateSerializer, VideoSerializer


# Create your views here

# pylint: disable=too-many-ancestors
class ImageGalleryViewSet(viewsets.ModelViewSet):
    """
    The ImageGalleryViewSet handles CRUD operations for the ImageGallery model
    """
    queryset = ImageGallery
    http_method_names = ['get', 'post', 'put', 'delete']
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        The get_serializer_class returns a serializer class based on the action performed
        """
        if self.action == 'create':
            return ImageGalleryCreateSerializer
        if self.action == 'update':
            return ImageGalleryUpdateSerializer
        return ImageGallerySerializer

    def get_queryset(self):
        """
        The get_queryset method returns a queryset of ImageGallery Model
        """
        user = self.request.user.id
        return ImageGallery.objects.filter(user=user).order_by('-id')

    def list(self, request, *args, **kwargs):
        """
        The list retrieves all instances of the ImageGallery model
        """
        if not self.get_queryset().exists():
            return Response(
                {"message": VALIDATION['image_gallery_set']['no_album']}, status=status.HTTP_200_OK
            )
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        This method retrieves a single instance of the ImageGallery model
        using the provided primary key (pk)
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        This method creates a new instance of the ImageGallery model using validated serializer data
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            image_gallery = serializer.create(serializer.validated_data)
            return Response({'message': SUCCESS_MESSAGES['IMAGE_GALLERY']['CREATED_SUCCESSFULLY'],
                             'data': {
                                 'id': image_gallery.id,
                                 'gallery': image_gallery.gallery_name,
                                 'created_at': image_gallery.created_at,
                             }}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        This method creates a new instance of the ImageGallery model using validated serializer data
        and the primary key of the instance to be updated
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            image_gallery = serializer.update(instance, serializer.validated_data)
            return Response({'message': SUCCESS_MESSAGES['IMAGE_GALLERY']['UPDATED_SUCCESSFULLY'],
                             'data': {
                                 'id': image_gallery.id,
                                 'gallery': image_gallery.gallery_name,
                                 'created_at': image_gallery.created_at,
                                 'updated_at': image_gallery.updated_at,
                             }},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        This method deletes an instance of the ImageGallery model using the primary key
        It also deletes the associated gallery folder if it exists.
        """
        instance = self.get_object()
        user = request.user
        folder_path = IMAGE_GALLERY_PATH.format(
            username=user.username, gallery_name=instance.gallery_name
        )
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        instance.delete()
        return Response({'message': SUCCESS_MESSAGES['IMAGE_GALLERY']['DELETED_SUCCESSFULLY']},
                        status=status.HTTP_200_OK)


class ImageViewSet(viewsets.ModelViewSet):
    """
    The ImageViewSet handles Create and Delete operations for the Image model
    """
    queryset = Image
    http_method_names = ['get', 'post', 'delete']
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        """
        The get_serializer_class returns a serializer class based on the action being performed
        """
        if self.action == 'create':
            return ImageCreateSerializer
        return ImageSerializer

    def get_queryset(self):
        """
        The get_queryset method returns a queryset of Image Model
        """
        user = self.request.user.id
        return Image.objects.filter(image_gallery__user=user).order_by('-id')

    def list(self, request, *args, **kwargs):
        """
        The list retrieves all instances of the Image model
        """
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": VALIDATION['image']['no_image']}, status=status.HTTP_200_OK
            )
        images = []
        for image in queryset:
            serializer = self.get_serializer(image)
            images.append(serializer.data)
        return Response(images, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        This method retrieves a single instance of the Image model
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        This method creates a new instance of the Image model
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            images = serializer.create(serializer.validated_data)

            response_data = []
            for image in images:
                image_url = request.build_absolute_uri(image.image.url)
                response_data.append({
                    'id': image.id,
                    'image': image_url,
                    'image_gallery_id': image.image_gallery_id,
                    'gallery': image.image_gallery.gallery_name,
                    'created_at': image.created_at,
                    'updated_at': image.updated_at,
                })
            return Response(
                {'message': SUCCESS_MESSAGES['IMAGE']['CREATED_SUCCESSFULLY'], 'data': response_data
                 },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        This method deletes an instance of the Image model using the primary key
        It also deletes the associated gallery folder if it exists.
        """
        instance = self.get_object()
        image_path = IMAGE_PATH_TEMPLATE.format(MEDIA_URL, instance.image.name)
        os.remove(image_path)
        instance.delete()
        return Response({'message': SUCCESS_MESSAGES['IMAGE']['DELETED_SUCCESSFULLY']},
                        status=status.HTTP_200_OK)


class VideoGalleryViewSet(viewsets.ModelViewSet):
    """
    The VideoGalleryViewSet handles CRUD operations for the VideoGallery model
    """
    queryset = VideoGallery
    http_method_names = ['get', 'post', 'put', 'delete']
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        The get_serializer_class returns a serializer class based on the action being performed
        """
        if self.action == 'create':
            return VideoGalleryCreateSerializer
        if self.action == 'update':
            return VideoGalleryUpdateSerializer
        return VideoGallerySerializer

    def get_queryset(self):
        """
        The get_queryset method returns a queryset of VideoGallery Model
        """
        user = self.request.user
        return VideoGallery.objects.filter(user=user).order_by('id')

    def list(self, request, *args, **kwargs):
        """
        The list retrieves all instances of the VideoGallery model
        """
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        This method retrieves a single instance of the VideoGallery model
        using the provided primary key (pk)
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        This method creates a new instance of the VideoGallery model using validated serializer data
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response({'message': SUCCESS_MESSAGES['VIDEO_GALLERY']['CREATED_SUCCESSFULLY'],
                             'data': serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        This method creates a new instance of the VideoGallery model using validated serializer data
        and the primary key of the instance to be updated
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.update(instance, serializer.validated_data)
            response_data = {'message': SUCCESS_MESSAGES['VIDEO_GALLERY']['UPDATED_SUCCESSFULLY'],
                             'data': serializer.data}
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        This method deletes an instance of the VideoGallery model using the primary key
        It also deletes the associated Video folder if it exists
        """
        instance = self.get_object()
        user = request.user
        username = user.get_username()
        folder_path = VIDEO_GALLERY_PATH.format(
            username=username, gallery_name=instance.gallery_name
        )
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        instance.delete()
        return Response({'message': SUCCESS_MESSAGES['VIDEO_GALLERY']['DELETED_SUCCESSFULLY']})


class VideoViewSet(viewsets.ModelViewSet):
    """
    The VideoViewSet handles Create and Delete operations for the Video model
    """
    queryset = Video
    http_method_names = ['get', 'post', 'delete']
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_class(self):
        """
        The get_serializer_class returns a serializer class based on the action being performed
        """
        if self.action == 'create':
            return VideoCreateSerializer
        return VideoSerializer

    def get_queryset(self):
        """
        The get_queryset method returns a queryset of video Model
        """
        user = self.request.user
        return Video.objects.filter(video_gallery__user=user).order_by('id')

    def list(self, request, *args, **kwargs):
        """
        The list retrieves all instances of the Video model
        """
        queryset = self.get_queryset()
        videos = []
        for video in queryset:
            serializer = self.get_serializer(video)
            videos.append(serializer.data)
        return Response(videos, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        This method retrieves a single instance of the Video model
        using the provided primary key (pk)
        """
        serializer = self.get_serializer(self.get_object())
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        This method creates a new instance of the Video model
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            videos = serializer.create(serializer.validated_data)
            response_data = []
            for video in videos:
                video_url = request.build_absolute_uri(video.video.url)
                response_data.append({
                    'id': video.id,
                    'video': video_url,
                    'video_gallery_id': video.video_gallery_id,
                    'gallery': video.video_gallery.gallery_name,
                    'created_at': video.created_at,
                    'updated_at': video.updated_at,
                })
            return Response(
                {'message': SUCCESS_MESSAGES['VIDEO']['CREATED_SUCCESSFULLY'], 'data': response_data
                 },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        This method deletes an instance of the Video model using the primary key
        It also deletes the associated video folder if it exists
        """
        instance = self.get_object()
        video_path = VIDEO_PATH_TEMPLATE.format(MEDIA_URL, instance.video.name)
        os.remove(video_path)
        instance.delete()
        return Response({'message': SUCCESS_MESSAGES['VIDEO']['DELETED_SUCCESSFULLY']})
