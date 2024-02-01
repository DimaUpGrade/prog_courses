from rest_framework import serializers
from .models import Course, UserCourse, Comment, Review, Platform, Author, Tag
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError


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


class UserCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCourse
        fields = '__all__'


class UserPartialSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username',)


class UserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user = UserPartialSerializer(many=False, read_only=True)

    class Meta:
        model = Review
        fields = ('id_course', 'user', 'rating', 'text_review', 'creation_date')


class CommentSerializer(serializers.ModelSerializer):
    user = UserPartialSerializer(many=False, read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'id_course', 'user', 'commentary_text', 'creation_date', 'likes')


class CourseSerializer(serializers.ModelSerializer):
    users = UserCourseSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=False)
    author = AuthorSerializer(many=False, read_only=False)
    platform = PlatformSerializer(many=False, read_only=False)
    publisher = UserPartialSerializer(many=False, read_only=False)
    reviews = ReviewSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        #
        # Check this:
        # fields = '__all__'
        #
        fields = ('id', 'title', 'description', 'author', 'platform', 'publisher', 'link', 'verified', 'tags', 'users', 'reviews', 'comments')
