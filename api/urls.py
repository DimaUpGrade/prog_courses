from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'courses', CourseViewSet, basename='course')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'comments', CommentViewSet, basename='comment')

# router.register(r'course_comments, CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('registration/', UserRegistration.as_view(), name='registration'),
    path('login/', UserLogin.as_view(), name='login'),
    path('is_username_taken/', IsUsernameTaken.as_view(), name='is_username_taken'),
    path('account/', UserView.as_view(), name='account'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('courses/<int:pk>/comments/', CourseCommentsAPIView.as_view(), name='course_comments'),
    path('courses/<int:pk>/reviews/', CourseReviewsAPIView.as_view(), name='course_reviews'),
    path('platforms/', PlatformListAPIView.as_view(), name='platforms'),
]