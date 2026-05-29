from django.urls import path

from courses.views import (
    CourseListAPIView,
    CourseDetailAPIView,
    ContactUsAPIView,
    CategoryListAPIView,
    CategoryDetailAPIView,
    CommentListAPIView,
    CommentCreateAPIView,
    CourseLessonListAPIView,
    MyCourseListAPIView,
    CourseStudentListAPIView,
    EnrollCourseAPIView,
)

urlpatterns = [
    path("courses/", CourseListAPIView.as_view()),
    path("courses/<str:course_slug>/lessons", CourseLessonListAPIView.as_view()),
    path("contactus/", ContactUsAPIView.as_view()),
    path("categories/", CategoryListAPIView.as_view()),
    path("courses/<slug:slug>/", CourseDetailAPIView.as_view()),
    path("categories/<slug:slug>/", CategoryDetailAPIView.as_view()),
    path("courses/<slug:course_slug>/comments/", CommentListAPIView.as_view()),
    path("courses/<slug:course_slug>/comments/create/", CommentCreateAPIView.as_view()),
    path("my/courses/", MyCourseListAPIView.as_view()),
    path("courses/<slug:course_slug>/students/", CourseStudentListAPIView.as_view()),
    path("courses/<slug:course_slug>/enroll/", EnrollCourseAPIView.as_view()),
]
