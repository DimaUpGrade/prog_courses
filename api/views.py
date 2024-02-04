from django.contrib.auth import login, logout
from django.shortcuts import render, get_object_or_404, get_list_or_404
from rest_framework.authtoken.models import Token
import rest_framework.permissions as perms
from rest_framework import generics, status, viewsets
from .models import (
    Course, 
    UserCourse, 
    Comment, 
    Review, 
    Platform, 
    Author, 
    Tag
)
from .serializers import (
    UserRegistrationSerializer, 
    UsernameSerializer,
    UserLoginSerializer,
    CourseSerializer,
    ReviewSerializer,
    CommentSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response

# from rest_framework_filters import filters as filters
from django_filters.rest_framework import DjangoFilterBackend

from .service import CourseTagsFilter, ReviewsCourseFilter, CommentsCourseFilter



class UserRegistration(APIView):
    permission_classes = [perms.AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.create(request.data)
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'Bad request': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)


class IsUsernameTaken(APIView):
    permission_classes = [perms.AllowAny]
    serializer_class = UsernameSerializer

    def post(self, request):
        serializer = UsernameSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"Username is valid": "Username is valid"}, status=status.HTTP_200_OK)
        return Response({"Username is taken": "Username is taken or something wrong"}, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = [perms.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(request.data)
            login(request, user)
            return Response({'Token': Token.objects.get_or_create(user=user)[0].key}, status=status.HTTP_200_OK)


class UserLogout(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('platform', 'author', 'publisher').prefetch_related('tags', 'users')
    serializer_class = CourseSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CourseTagsFilter

    # # Example of overriding queryset method 
    # def get_queryset(self):
    #     pk = self.kwargs.get("pk")

    #     if not pk:
    #         return Course.objects.all()
        
    #     return Course.objects.filter(pk=pk)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'id_course')
    serializer_class = ReviewSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = ReviewsCourseFilter


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('user', 'id_course')
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CommentsCourseFilter


