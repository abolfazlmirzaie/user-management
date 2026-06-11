from courses.models import Course
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    message = "You are not Instructor"

    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "instructors")


class IsCourseInstructor(BasePermission):
    message = "You are not Instructor of this course"

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if not hasattr(request.user, "instructors"):
            return False

        course_slug = view.kwargs.get("course_slug")
        if course_slug:
            course = get_object_or_404(Course, slug=course_slug)
            return course.instructor.user == request.user

        return True
