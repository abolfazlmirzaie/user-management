from django.urls import path

from courses.views import CourseListAPIView

urlpatterns = [
    path('course-list/', CourseListAPIView.as_view()),
]