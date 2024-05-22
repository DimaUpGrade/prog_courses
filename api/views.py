from django.contrib.auth import login, logout
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.db.models import Count, F, Q, ExpressionWrapper, Value, OuterRef, Case, When, Exists, Sum, CharField
from django.db.models.functions import Lower
from django.db import models
from rest_framework.authtoken.models import Token
import rest_framework.permissions as perms
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework import generics, status, viewsets
from .models import (
    Course,  
    Comment, 
    Review, 
    Platform, 
    Author, 
    Tag,
    SearchWord,
    NewsPost,
    Report
)
from .serializers import (
    UserRegistrationSerializer, 
    UsernameSerializer,
    UserLoginSerializer,
    CourseSerializer,
    ReviewSerializer,
    CommentSerializer,
    CreateCommentSerializer,
    UserFullSerializer,
    CreateReviewSerializer,
    CreateCourseSerializer,
    PlatformSerializer,
    UserCourseSerializer,
    SearchResultsSerializer,
    NewsPostSerializer,
    CreateNewsPostSerializer,
    TagSerializer,
    ReportSerializer,
    CreateReportSerializer
)
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
import rest_framework.permissions as perms

# from rest_framework_filters import filters as filters
from django_filters.rest_framework import DjangoFilterBackend
from .service import CourseFilter, ReviewsCourseFilter, CommentsCourseFilter
from .search import SearchWordsConverter

CharField.register_lookup(Lower)

def recalculate_rating(course):
    reviews = list(course.reviews.all())
    points = 0
    count = len(reviews)
    
    for review in reviews:
        points += review.rating

    rating = round(points / count, 2)
    course.rating = rating
    course.save()
    

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
            try:
                user = serializer.check_user(request.data)
            except:
                return Response({"Bad request:": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
            
                
            if user:
                login(request, user)
                return Response({'Token': Token.objects.get_or_create(user=user)[0].key}, status=status.HTTP_200_OK)
        return Response({"Error:": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    permission_classes = [perms.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class PlatformListAPIView(generics.ListAPIView):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    filter_backends = (DjangoFilterBackend, )


class CourseViewSet(viewsets.ModelViewSet):
    # queryset = Course.objects.select_related('platform', 'author', 'publisher').prefetch_related('tags', 'search_words').annotate(sum_weight=Value(0, models.IntegerField()))
    queryset = Course.objects.select_related('platform', 'author', 'publisher').prefetch_related('tags').annotate(in_favorite=Value(False, models.BooleanField())).filter(verified=True)
    serializer_class = CourseSerializer
    create_serializer_class = CreateCourseSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CourseFilter
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().prefetch_related('search_words'))
        
        # Searching by courses
        if request.GET.get('search_query'):
            search_query = request.GET.get('search_query')
            search_words_obj = SearchWordsConverter(search_query)
            search_words = search_words_obj.get_search_words_list()
            search_words.append(search_query)
            
            queryset = self.get_queryset().filter(search_words__title__in=search_words).annotate(sum_weight=Sum(F('search_words__weight'), filter=Q(search_words__title__in=search_words))).order_by('-sum_weight')

            if request.GET.get('tag'):
                query_tags = request.GET.get('tag')
                if ',' in query_tags:
                    query_tags = query_tags.split(',')
                    queryset = queryset.filter(tags__title__in=query_tags)
                else:
                    queryset = queryset.filter(tags__title__in=[query_tags])
                # try:
                #     search_tag = Tag.objects.get(title=request.GET.get('tag'))
                #     queryset = queryset.filter(tags__in=search_tag)
                # except Tag.DoesNotExist:
                #     queryset = queryset.filter(tags__in=search_tag)
            
            if request.GET.get('only_free'):
                if request.GET.get('only_free') == 'true':
                    queryset = queryset.filter(paid=False)
            
            page = self.paginate_queryset(queryset)
            serializer = SearchResultsSerializer(page, many=True)
        else:
            if request.GET.get('tag'):
                query_tags = request.GET.get('tag')
                if ',' in query_tags:
                    query_tags = query_tags.split(',')
                    queryset = queryset.filter(tags__title__in=query_tags)
                else:
                    queryset = queryset.filter(tags__title__in=[query_tags])
                    
            if request.GET.get('only_free'):
                if request.GET.get('only_free') == 'true':
                    queryset = queryset.filter(paid=False)
                    
            page = self.paginate_queryset(queryset)
            serializer = self.get_serializer(page, many=True)
            
        if page is not None:
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        # course = get_object_or_404(Course, id=pk)
        user = self.request.user
        
        try:
            if isinstance(user, AnonymousUser):
                course = Course.objects.annotate(in_favorite=Value(True, models.BooleanField())).get(id=pk)
            else:
                course = Course.objects.annotate(in_favorite = Sum(
                    Case(
                        When(
                            users__in=[user.id],
                            then=Value(True)
                        ),
                        default=Value(False),
                        output_field=models.BooleanField()
                    )
                )).get(id=pk)
                
            
            serializer = self.get_serializer(course)
            return Response(serializer.data)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['get'], permission_classes=[perms.IsAuthenticated])
    def is_review_exists(self, request, pk=None):
        user = self.request.user
        course = get_object_or_404(Course, pk=pk)
        
        try:
            entry = Review.objects.select_related('user', 'id_course').annotate(likes_count=Count(F('likes'))).annotate(is_liked=Value(False, models.BooleanField())).get(id_course=course, user=user)
            result = ReviewSerializer(entry).data 
            response = Response(result)
        except Review.DoesNotExist:
            response = Response(False)

        return response
    
    @action(detail=True, methods=['patch'], permission_classes=[perms.IsAuthenticated])
    def add_to_favorite(self, request, pk=None):
        user = self.request.user
        course = get_object_or_404(Course, pk=pk)
        
        if user in course.users.all():
            course.users.remove(user)
        else:
            course.users.add(user)
        
        return Response(status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        serializer = self.create_serializer_class(data=request.data)
        # print(request.data)
        if serializer.is_valid(raise_exception=True):
            user = self.request.user
            if isinstance(user, AnonymousUser):
                response = Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                title = serializer.data.get('title')
                description = serializer.data.get('description')
                link = serializer.data.get('link')
                price = serializer.data.get('price')

                try:
                    course = Course.objects.get(link=link)
                    return Response({'Bad Request': 'This course is already exists!'}, status=status.HTTP_400_BAD_REQUEST)
                except Course.DoesNotExist:
                    if price == 0:
                        paid = False
                    else:
                        paid = True

                    author_link = request.data["author_link"]
                    author_username = request.data["author_username"]

                    try:
                        author = Author.objects.get(link=author_link)
                    except Author.DoesNotExist:
                        
                        author = Author(username=author_username, link=author_link)
                        author.save()

                    try:
                        platform = Platform.objects.get(title__lower=request.data["platform"])
                    except Platform.DoesNotExist:
                        platform = Platform(title=request.data["platform"])
                        platform.save()                    

                    course = Course(title=title, description=description, link=link, price=price, paid=paid, author=author, platform=platform, publisher=user)
                    course.save()
                    
                    search_words_obj = SearchWordsConverter(title)
                    search_words = search_words_obj.get_search_words_list_with_weight()
                    search_words.extend([[title, 20], [author_username, 10]])
                    
                    for item in search_words:
                        
                        ###
                        try:
                            search_word = SearchWord.objects.get(title=item[0])
                        except SearchWord.DoesNotExist:
                            search_word = SearchWord(title=item[0], weight=item[1])
                        ###
                        
                        
                        # search_word = SearchWord(title=item[0], weight=item[1])
                        search_word.save()
                            
                        course.search_words.add(search_word)
                            
                    
                    
                    response = Response("Course has been added", status=status.HTTP_201_CREATED)
        else:
            response = Response({'Bad Request': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

        return response


class ReviewViewSet(viewsets.ModelViewSet):
    # не нужно id_course возвращать
    # queryset = Review.objects.select_related('user', 'id_course').order_by('-likes')
    queryset = Review.objects.select_related('user').annotate(likes_count=Count(F('likes'))).annotate(is_liked=Value(False, models.BooleanField())).order_by('-likes_count')
    serializer_class = ReviewSerializer
    create_serializer_class = CreateReviewSerializer
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

    
    ###
    def create(self, request, *args, **kwargs):
        serializer = self.create_serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            # Check, if course exists
            if id_course := serializer.data.get('id_course'):
                course = get_object_or_404(Course, pk=id_course)
                user = self.request.user

                # Check, if user is not AnonymousUser
                if isinstance(user, AnonymousUser):
                    response = Response(status=status.HTTP_401_UNAUTHORIZED)
                else:
                    # Check, if user has already sended review for this course
                    try:
                        entry = Review.objects.select_related('user', 'id_course').annotate(likes_count=Count(F('likes'))).annotate(is_liked=Value(False, models.BooleanField())).get(
                            id_course=course,
                            user=user)
                        response = Response({'Bad Request': 'This user has already sended review for this course!'}, status=status.HTTP_400_BAD_REQUEST)

                    except Review.DoesNotExist:
                        text_review = serializer.data.get('text_review')
                        rating = serializer.data.get('rating')
                        if rating <= 10 and rating >= 1:
                            rating = round(rating)
                            review = Review(id_course=course, text_review=text_review, user=user, rating=rating)
                            review.save()
                            
                            recalculate_rating(course)
                            
                            response = Response("Review has been created", status=status.HTTP_201_CREATED)
                        else:
                            response = Response({'Bad Request': 'Invalid rating data'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                response = Response({'Bad Request': 'Invalud course id'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = Response({'Bad Request': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
        
        return response
    ###

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
        
        if isinstance(user, AnonymousUser):
            reviews = course.reviews.annotate(likes_count=Count(F('likes'))).annotate(is_liked=Value(False, models.BooleanField())).order_by('-likes_count')
        else:
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


class UserCoursesAPIView(APIView):
    pagination_class = LimitOffsetPagination()
    serializer_class = UserCourseSerializer
    permission_classes = [perms.IsAuthenticated]

    def paginate(self, queryset):
        result_page = self.pagination_class.paginate_queryset(queryset, self.request, self)
        serializer = self.serializer_class(result_page, many=True)
        return self.pagination_class.get_paginated_response(serializer.data)

    def get(self, request, *args, **kwargs):
        user = self.request.user
        # user = User.objects.get(username='dimau')
        
        # # Если будет нужно вернуть in_favorite для курса 
        # user_courses = user.course_users.annotate(in_favorite = Sum(
        #             Case(
        #                 When(
        #                     users__in=[user.id],
        #                     then=Value(True)
        #                 ),
        #                 default=Value(False),
        #                 output_field=models.BooleanField()
        #             )
        #         )).all()
        
        user_courses = user.course_users.all()
        response = self.paginate(user_courses)
        return response
        

class NewsPostViewSet(viewsets.ModelViewSet):
    serializer_class = NewsPostSerializer
    queryset = NewsPost.objects.select_related('user').order_by('-creation_date')
    create_serializer_class = CreateNewsPostSerializer
    filter_backends = (DjangoFilterBackend, )


class TagViewSet(viewsets.ModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    http_method_names = ['get']
    filter_backends = (DjangoFilterBackend, )
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().order_by('title'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ReportViewSet(viewsets.ModelViewSet):
    serializer_class = ReportSerializer
    create_serializer_class = CreateReportSerializer
    filter_backends = (DjangoFilterBackend, )
    queryset = Report.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.create_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)