"""
This view contain the SignupView, SigninView, SignOutView,
UsernameValidatorView, EmailValidatorView, UserProfileView.
These views are called by router to perform respective
functionalities that are defines inside that particular view.
"""
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .messages import SUCCESS_MESSAGE, ERROR_MESSAGE
from .serializers import SignupSerializer, SigninSerializer, UsernameValidatorSerializer, \
    EmailValidatorSerializer, SignOutSerializer, UserProfileSerializer
from .models import User


# pylint: disable=too-many-ancestors
class SignupView(viewsets.ModelViewSet):
    """
    SignupView class to register a new user
    """
    queryset = User
    serializer_class = SignupSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        """
        creates a new requested user
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SigninView(viewsets.ModelViewSet):
    """
    Allow only authenticated user to signin.
    If the user is valid provide him the access and refresh token
    and save it to the database.
    """
    queryset = User.objects.filter()
    serializer_class = SigninSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.create(serializer.validated_data)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


class SignOutView(viewsets.ModelViewSet):
    """
    Allow only signin user to sign out
    This Api perform the functionality to blacklist the refresh
    token to avoid access of unauthenticated user
    """
    serializer_class = SignOutSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.create(serializer.validated_data)
            return Response(data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class EmailValidatorView(viewsets.ModelViewSet):
    """
    ValidateView class to Validate email at runtime
    """
    queryset = User
    serializer_class = EmailValidatorSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        """
        get queryset of User Model
        """
        return User.objects.filter(email="email")

    def retrieve(self, request, *args, **kwargs):
        """
        get an instance of user and validate it using serializer class
        """
        serializer = self.serializer_class(data=request.GET)
        if serializer.is_valid(raise_exception=True):
            return Response(data={
                'success': True, 'validated_data': serializer.validated_data
            }, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)


class UsernameValidatorView(viewsets.ModelViewSet):
    """
    UsernameValidatorView class to Validate username at runtime
    """
    queryset = User.objects.filter(username="username")
    serializer_class = UsernameValidatorSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        """
        get queryset of User Model
        """
        return User.objects.filter(username="username")

    def retrieve(self, request, *args, **kwargs):
        """
        get an instance of user and validate it using serializer class
        """
        serializer = self.serializer_class(data=request.GET)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(viewsets.ModelViewSet):
    """
    This view perform retrieving the data of the logged-in user
    and update their data according to their provided values.
    """
    queryset = User
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch']

    def get_queryset(self):
        """
        The get_queryset method returns a queryset of User objects that
        includes only the currently authenticated user.
        """
        return User.objects.filter(id=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        """
        Display the single instance of the User
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        :param request: It gets the data that is requested by the user
        :param args: This returns the validated data in the form of list
        :param kwargs: This return the validated data in the form of dictionary
        :return: This return the updated data to the user with status
        """
        userprofile = self.get_object()
        serializer = self.serializer_class(userprofile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.update(userprofile, serializer.validated_data)
            return Response({
                'message': SUCCESS_MESSAGE['success'],
                'data': serializer.data,
            }, status=status.HTTP_200_OK)
        return Response({
            'error': ERROR_MESSAGE['error']
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        :param request: It gets the data that is requested by the user
        :param args: This returns the validated data in the form of list
        :param kwargs: This return the validated data in the form of dictionary
        :return: This return the updated data to the user with status
        """
        userprofile = self.get_object()
        serializer = self.serializer_class(userprofile, data=request.data)
        if serializer.is_valid():
            serializer.update(userprofile, serializer.validated_data)
            return Response({
                'message': SUCCESS_MESSAGE['success'],
                'data': serializer.data,
            }, status=status.HTTP_200_OK)
        return Response({
            'error': ERROR_MESSAGE['error']
        }, status=status.HTTP_400_BAD_REQUEST)
