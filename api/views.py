from django.contrib.auth import login, logout
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.db.models import Count, F, Q, ExpressionWrapper, Value, OuterRef, Case, When, Exists, Sum
from django.db import models
from rest_framework.authtoken.models import Token
import rest_framework.permissions as perms
from rest_framework.decorators import action
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
    CreateCommentSerializer,
    UserFullSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
import rest_framework.permissions as perms

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
    permission_classes = [perms.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('platform', 'author', 'publisher').prefetch_related('tags')
    serializer_class = CourseSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CourseTagsFilter
    
    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        course = get_object_or_404(Course, id=pk)
        serializer = self.get_serializer(course)
        return Response(serializer.data)
    
    # def get_queryset(self):
    #     print(self.request)
    #     queryset = self.request.course
        
    #     course = get_object_or_404(queryset)
    #     return course

    # # # Example of overriding queryset method 
    # def get_queryset(self, *args, **kwargs):
    #     pk = self.kwargs.get("pk")

    #     if not pk:
    #         return Course.objects.all()
        
    #     return get_object_or_404(Course.objects.filter(pk=pk))


class ReviewViewSet(viewsets.ModelViewSet):
    # не нужно id_course возвращать
    # queryset = Review.objects.select_related('user', 'id_course').order_by('-likes')
    # queryset = Review.objects.select_related('user').order_by('-likes')
    queryset = Review.objects.select_related('user').annotate(likes_count=Count(F('likes'))).order_by('-likes_count')
    serializer_class = ReviewSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = ReviewsCourseFilter

    @action(detail=True, methods=['post'], permission_classes=[perms.IsAuthenticated])
    def like_review(self, request, pk=None):
        user = self.request.user
        review = Review.objects.get(pk=pk)
        if user not in review.likes.all():
            review.likes.add(user)
        else:
            review.likes.remove(user)
        review.save()
        return Response(status=status.HTTP_200_OK)


class CourseReviewsAPIView(APIView):
    # queryset = Course.objects.all()
    pagination_class = LimitOffsetPagination()
    permission_classes = [perms.IsAuthenticatedOrReadOnly]

    def paginate(self, queryset):
        result_page = self.pagination_class.paginate_queryset(queryset, self.request, self)
        serializer = ReviewSerializer(result_page, many=True)
        return self.pagination_class.get_paginated_response(serializer.data)

    def get(self, request, *args, **kwargs):
        # course = Course.objects.get(id=self.kwargs["pk"])
        
        user = self.request.user
        pk = self.kwargs.get("pk")
        course = get_object_or_404(Course, id=pk)
        # reviews = course.reviews.annotate(likes_count=Count(F('likes'))).order_by('-likes_count')
        
        ###
        if isinstance(user, AnonymousUser):
            reviews = course.reviews.annotate(likes_count=Count(F('likes'))).annotate(is_liked=Value(False, models.BooleanField())).order_by('-likes_count')
        else:
            # print(self.request.user)
            # reviews = course.reviews.annotate(likes_count=Count(F('likes'))).annotate(is_liked=ExpressionWrapper(
            #         Q(Q(likes=user)| Q(likes=None)), output_field=models.BooleanField()
            #         )).order_by('-likes_count')
            reviews = course.reviews.annotate(likes_count=Count(F('likes'))).annotate(
                is_liked = Sum(
                    Case(
                        When(
                            likes__in=[user.id],
                            then=Value(True)
                        ),
                        default=Value(False),
                        output_field=models.BooleanField()
                    )
                )
            ).order_by('-likes_count')

        
        response = self.paginate(reviews)
        return response
    

class CourseCommentsAPIView(APIView):
    # queryset = Course.objects.all()
    pagination_class = LimitOffsetPagination()
    permission_classes = [perms.IsAuthenticatedOrReadOnly]
    
    def paginate(self, queryset):
        result_page = self.pagination_class.paginate_queryset(queryset, self.request, self)
        serializer = CommentSerializer(result_page, many=True)
        return self.pagination_class.get_paginated_response(serializer.data)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        pk = self.kwargs.get("pk")
        course = get_object_or_404(Course, id=pk)
        # course = Course.objects.get(id=self.kwargs["pk"])

        # .order_by('-likes_count') has been removed for a while
        if isinstance(user, AnonymousUser):
            comments = course.comments.annotate(likes_count=Count(F('likes'))).annotate(is_liked=Value(False, models.BooleanField())).order_by('-creation_date')
        else:
            comments = course.comments.annotate(likes_count=Count(F('likes'))).annotate(
                is_liked = Sum(
                    Case(
                        When(
                            likes__in=[user.id],
                            then=Value(True)
                        ),
                        default=Value(False),
                        output_field=models.BooleanField()
                    )
                )
            ).order_by('-creation_date')

        # course = get_object_or_404(Course, id=pk)
        response = self.paginate(comments)
        return response


class CommentViewSet(viewsets.ModelViewSet):
    # queryset = Comment.objects.select_related('user', 'id_course').order_by('-likes')
    queryset = Comment.objects.select_related('user').annotate(likes_count=Count(F('likes'))).annotate(is_liked=Value(False, models.BooleanField())).order_by('-likes_count')
    serializer_class = CommentSerializer
    create_serializer_class = CreateCommentSerializer
    permission_classes = [perms.IsAuthenticatedOrReadOnly]
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CommentsCourseFilter

    @action(detail=True, methods=['post'], permission_classes=[perms.IsAuthenticated])
    def like_comment(self, request, pk=None):
        user = self.request.user
        comment = Comment.objects.get(pk=pk)
        if user not in comment.likes.all():
            comment.likes.add(user)
        else:
            comment.likes.remove(user)
        comment.save()
        return Response(status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.create_serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            if id_course := serializer.data.get('id_course'):
                course = get_object_or_404(Course, pk=id_course)
            user = self.request.user
            commentary_text = serializer.data.get('commentary_text')
            comment = Comment(id_course=course, commentary_text=commentary_text, user=user)
            comment.save()
            
            return Response("Comment has been created", status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        


class UserView(APIView):
    permission_classes = [perms.IsAuthenticated]
    serializer_class = UserFullSerializer

    def get(self, request):
        serializer = UserFullSerializer(request.user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)
    
