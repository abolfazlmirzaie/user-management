from django.urls import path

from courses.views import CourseListAPIView

urlpatterns = [
    path("courses/", CourseListAPIView.as_view()),
]
