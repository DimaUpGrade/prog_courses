from rest_framework import serializers
from .models import Course, UserCourse, Comment, Review, Platform, Author, Tag
from django.contrib.auth.models import User


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
