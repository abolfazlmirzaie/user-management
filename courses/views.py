from .models import Course
from rest_framework.generics import ListAPIView
from .pagination import CoursePageNumberPagination
from . serializers import CourseSerializer
from django.contrib.postgres.search import TrigramSimilarity


class CourseListAPIView(ListAPIView):
    serializer_class = CourseSerializer
    pagination_class = CoursePageNumberPagination
    ordering_fields = ["created_at", "title", "level"]

    def get_queryset(self):
        queryset = Course.objects.all() \
            .select_related("teacher")

        search = self.request.query_params.get("search")

        if search and len(search) > 2:
            queryset = queryset.annotate(
                similarity=TrigramSimilarity("title", search)
            ).filter(similarity__gt=0.2).order_by("-similarity")

        level = self.request.query_params.get("level")
        if level:
            queryset = queryset.filter(level=level)

        category = self.request.query_params.get("category")
        if category:
            categories = [c for c in category.split(",") if c.strip()]
            if categories:
                queryset = queryset.filter(categories__slug__in=categories)

        return queryset