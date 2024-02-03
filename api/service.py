from django_filters import rest_framework as filters
from .models import *


class CharFieldInFilter(filters.BaseInFilter, filters.CharFilter):
    pass

class CourseTagsFilter(filters.FilterSet):
    tags = CharFieldInFilter(field_name='tags__title', lookup_expr='in')

    class Meta:
        model = Course
        fields = ['tags']
