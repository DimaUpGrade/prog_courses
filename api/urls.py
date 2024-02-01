from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'courses', CourseViewSet, basename='course')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]