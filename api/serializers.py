from rest_framework import serializers
from .models import Course, Comment, Review, Platform, Author, Tag, SearchWord, Report, NewsPost
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.db.models import Count


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user_obj = User.objects.create_user(email=validated_data['email'], username=validated_data['username'],
                                            password=validated_data['password'])
        user_obj.save()
        token = Token.objects.create(user=user_obj)
        return user_obj


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def check_user(self, validated_data):
        user = authenticate(username=validated_data['username'], password=validated_data['password'])
        if not user:
            raise ValidationError('User not found.')
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class PlatformSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Platform
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class UsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class UserPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)


class UserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id_course', 'text_review', 'rating')


class ReviewSerializer(serializers.ModelSerializer):
    user = UserPartialSerializer(many=False, read_only=True)
    likes_count = serializers.IntegerField()
    is_liked = serializers.BooleanField()

    class Meta:
        model = Review
        fields = ('id', 'id_course', 'user', 'rating', 'text_review', 'creation_date', 'likes_count', 'is_liked')


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id_course', 'commentary_text')


class CommentSerializer(serializers.ModelSerializer):
    user = UserPartialSerializer(many=False, read_only=True)
    likes_count = serializers.IntegerField()
    is_liked = serializers.BooleanField()

    class Meta:
        model = Comment
        fields = ('id', 'id_course', 'user', 'commentary_text', 'creation_date', 'likes_count', 'is_liked')


class SearchWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchWord
        fields = '__all__'


class SearchResultsSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=False)
    search_words = SearchWordSerializer(many=True, read_only=False)
    author = AuthorSerializer(many=False, read_only=False)
    platform = PlatformSerializer(many=False, read_only=False)
    publisher = UserPartialSerializer(many=False, read_only=False)
    sum_weight = serializers.IntegerField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'cost', 'description', 'author', 'platform', 'publisher', 'link', 'verified', 'tags', 'search_words', 'sum_weight')


class CourseSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=False)
    author = AuthorSerializer(many=False, read_only=False)
    platform = PlatformSerializer(many=False, read_only=False)
    publisher = UserPartialSerializer(many=False, read_only=False)
    in_favorite = serializers.BooleanField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'cost', 'description', 'author', 'platform', 'publisher', 'link', 'verified', 'tags', 'in_favorite')


class UserCourseSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=False)
    author = AuthorSerializer(many=False, read_only=False)
    platform = PlatformSerializer(many=False, read_only=False)
    # in_favorite = serializers.BooleanField()

    class Meta:
        model = Course
        fields = ('id', 'title', 'paid', 'cost', 'author', 'platform', 'link', 'tags')


class CreateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('title', 'description', 'link', 'cost')


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = '__all__'


class CreateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('header', 'report_text')

        
class NewsPostSerializer(serializers.ModelSerializer):
    likes_count = serializers.IntegerField()
    is_liked = serializers.BooleanField()
    user = UserPartialSerializer(many=False, read_only=False)
    
    class Meta:
        model = NewsPost
        fields = ('header', 'post_text', 'user', 'creation_date', 'likes_count', 'is_liked')


class CreateNewsPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = ('header', 'post_text')