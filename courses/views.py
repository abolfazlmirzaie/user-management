from django.shortcuts import redirect
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, ContactUs, Category, Comment, Lesson, Enrollment
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from .pagination import CoursePageNumberPagination
from .serializers import (
    CourseSerializer,
    CourseDetailSerializer,
    ContactUsSerializer,
    CategorySerializer,
    CategoryDetailSerializer,
    CommentSerializer,
    LessonSerializer,
    EnrollmentSerializer,
)
from django.contrib.postgres.search import TrigramSimilarity
from users.throttles import LoginThrottle


class CourseListAPIView(ListAPIView):
    serializer_class = CourseSerializer
    pagination_class = CoursePageNumberPagination
    ordering_fields = ["created_at", "title", "level"]

    def get_queryset(self):
        queryset = Course.objects.all().select_related("teacher")

        search = self.request.query_params.get("search")

        if search and len(search) > 2:
            queryset = (
                queryset.annotate(similarity=TrigramSimilarity("title", search))
                .filter(similarity__gt=0.2)
                .order_by("-similarity")
            )

        level = self.request.query_params.get("level")
        created_at = self.request.query_params.get("created_at")
        if level:
            queryset = queryset.filter(level=level)
        if created_at:
            queryset = queryset.filter(created_at=created_at)

        category = self.request.query_params.get("category")
        if category:
            categories = [c for c in category.split(",") if c.strip()]
            if categories:
                queryset = queryset.filter(categories__slug__in=categories)

        return queryset


class CourseDetailAPIView(RetrieveAPIView):
    serializer_class = CourseDetailSerializer
    queryset = Course.objects.all()
    lookup_field = "slug"


class ContactUsAPIView(ListAPIView):
    serializer_class = ContactUsSerializer
    queryset = ContactUs.objects.all()


class CategoryListAPIView(ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()


class CategoryDetailAPIView(RetrieveAPIView):
    serializer_class = CategoryDetailSerializer
    queryset = Category.objects.all()
    lookup_field = "slug"


class CommentListAPIView(ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        course_slug = self.kwargs["course_slug"]

        if course_slug:
            try:
                course = Course.objects.get(slug=course_slug)
                return Comment.objects.filter(
                    course=course, parent=None, is_approved=True
                ).order_by("-created_at")
            except Course.DoesNotExist:
                raise NotFound("Course does not exist")
        else:
            raise NotFound("Course slug is required")


class CommentCreateAPIView(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [LoginThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request

        parent_id = self.request.data.get("parent_id")
        if parent_id:
            try:
                parent_comment = Comment.objects.filter(id=parent_id)
                context["parent_id"] = parent_comment.first().id

            except Comment.DoesNotExist:
                raise NotFound("Parent comment does not exist")

        else:
            context["parent_id"] = None
            return context


class CourseLessonListAPIView(ListAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        course_slug = self.kwargs["course_slug"]

        if not course_slug:
            raise NotFound("Course slug is required")

        course = Course.objects.get(slug=course_slug)

        lessons = Lesson.objects.filter(section__course=course).order_by(
            "section__title", "title"
        )
        return lessons


class EnrollCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_slug):

        try:
            course = Course.objects.get(slug=course_slug)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user = self.request.user

        if Enrollment.objects.filter(user=user, course=course).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        if course.is_premium:
            return redirect(request.META.get("HTTP_REFERER"))
        enrollment = Enrollment.objects.create(user=user, course=course)

        return Response(status=status.HTTP_201_CREATED)


class MyCourseListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        return Course.objects.filter(students__user=user)


class CourseStudentListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        course_slug = self.kwargs["course_slug"]

        if not course_slug:
            raise NotFound("Course slug is required")

        try:
            course = Course.objects.get(slug=course_slug)
        except Course.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            course = Course.objects.get(slug=course_slug)
            return Enrollment.objects.filter(course=course)
        except Course.DoesNotExist:
            return Enrollment.objects.none()
