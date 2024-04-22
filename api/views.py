from django.contrib.auth import login, logout
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.db.models import Count, F
from rest_framework.authtoken.models import Token
import rest_framework.permissions as perms
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
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
    CommentSerializer,
    UserFullSerializer,
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
        return Response({"Error:": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('platform', 'author', 'publisher').prefetch_related('tags')
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
    # не нужно id_course возвращать
    # queryset = Review.objects.select_related('user', 'id_course').order_by('-likes')
    # queryset = Review.objects.select_related('user').order_by('-likes')
    queryset = Review.objects.select_related('user').annotate(likes_count=Count(F('likes'))).order_by('-likes_count')
    serializer_class = ReviewSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = ReviewsCourseFilter


class CourseReviewsAPIView(APIView):
    queryset = Course.objects.all()
    pagination_class = LimitOffsetPagination()

    def paginate(self, queryset):
        result_page = self.pagination_class.paginate_queryset(queryset, self.request, self)
        serializer = ReviewSerializer(result_page, many=True)
        return self.pagination_class.get_paginated_response(serializer.data)

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(id=self.kwargs["pk"])
        reviews = course.reviews.annotate(likes_count=Count(F('likes'))).order_by('-likes_count')
        response = self.paginate(reviews)
        return response
    

class CourseCommentsAPIView(APIView):
    queryset = Course.objects.all()
    pagination_class = LimitOffsetPagination()
    
    def paginate(self, queryset):
        result_page = self.pagination_class.paginate_queryset(queryset, self.request, self)
        serializer = CommentSerializer(result_page, many=True)
        return self.pagination_class.get_paginated_response(serializer.data)

    def get(self, request, *args, **kwargs):
        course = Course.objects.get(id=self.kwargs["pk"])
        comments = course.comments.annotate(likes_count=Count(F('likes'))).order_by('-likes_count')
        response = self.paginate(comments)
        return response


class CommentViewSet(viewsets.ModelViewSet):
    # не нужно id_course возвращать
    # queryset = Comment.objects.select_related('user', 'id_course').order_by('-likes')
    queryset = Comment.objects.select_related('user').annotate(likes_count=Count(F('likes'))).order_by('-likes_count')
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CommentsCourseFilter


class UserView(APIView):
    permission_classes = [perms.IsAuthenticated]
    serializer_class = UserFullSerializer

    def get(self, request):
        serializer = UserFullSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

