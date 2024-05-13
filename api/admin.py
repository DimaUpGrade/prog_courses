from django.contrib import admin
from .models import Course, Comment, Review, Platform, Author, Tag, SearchWord, NewsPost, Report

admin.site.register(Course)
admin.site.register(Comment)
admin.site.register(Review)
admin.site.register(Platform)
admin.site.register(Author)
admin.site.register(Tag)
admin.site.register(SearchWord)
admin.site.register(NewsPost)
admin.site.register(Report)
