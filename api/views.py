from django.contrib.auth import login, logout
from django.shortcuts import render
from rest_framework import generics, status, viewsets
from .models import Course, UserCourse, Comment, Review, Platform, Author, Tag
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('platform', 'author', 'publisher').prefetch_related('tags', 'users', 'reviews', 'reviews__user', 'comments', 'comments__user')
    serializer_class = CourseSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'id_course')
    serializer_class = ReviewSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('user', 'id_course')
    serializer_class = CommentSerializer

