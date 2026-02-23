from .models import Course
from rest_framework.generics import ListAPIView
from . serializers import CourseSerializer


class CourseListAPIView(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

