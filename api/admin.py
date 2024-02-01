from django.contrib import admin
from .models import Course, UserCourse, Comment, Review, Platform, Author, Tag

admin.site.register(Course)
admin.site.register(UserCourse)
admin.site.register(Comment)
admin.site.register(Review)
admin.site.register(Platform)
admin.site.register(Author)
admin.site.register(Tag)
