from django_filters import rest_framework as filters
from .models import *


class CharFieldInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class NumberFieldInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass

# Multiple values in the same parameter can made by writing it twice
#
# For example, it works (!):
# ?platform=YouTube&?tags=VueJS&tags=JavaScript
#
class CourseTagsFilter(filters.FilterSet):
    tags = CharFieldInFilter(field_name='tags__title', lookup_expr='in')
    platform = CharFieldInFilter(field_name='platform__title', lookup_expr='in')

    class Meta:
        model = Course
        fields = ['tags', 'platform']


class ReviewsCourseFilter(filters.FilterSet):
    id_course = NumberFieldInFilter(field_name="id_course", lookup_expr='in')

    class Meta:
        model = Review
        fields = ['id_course']


class CommentsCourseFilter(filters.FilterSet):
    id_course = NumberFieldInFilter(field_name="id_course", lookup_expr='in')

    class Meta:
        model = Comment
        fields = ['id_course']



