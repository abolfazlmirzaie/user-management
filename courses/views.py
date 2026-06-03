from django.utils import timezone
from django.db.models import Prefetch
from django.shortcuts import redirect, get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Course,
    ContactUs,
    Category,
    Comment,
    Lesson,
    Enrollment,
    CourseLike,
    Section,
    LessonProgress,
)
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
    CourseProgressSerializer,
)
from django.contrib.postgres.search import TrigramSimilarity
from users.throttles import LoginThrottle
from users.services.user_service import EnrollmentService
from .services.course_service import ProgressService


class CourseListAPIView(ListAPIView):
    serializer_class = CourseSerializer
    pagination_class = CoursePageNumberPagination
    ordering_fields = ["created_at", "title", "level"]

    def get_queryset(self):
        queryset = (
            Course.objects.all()
            .select_related("instructor")
            .prefetch_related("categories", "likes")
        )

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
    queryset = Course.objects.select_related("instructor").prefetch_related(
        Prefetch("sections", queryset=Section.objects.prefetch_related("lessons")),
        "categories",
        "likes",
    )


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
            course = get_object_or_404(Course, slug=course_slug)
            return (
                Comment.objects.filter(course=course, parent=None, is_approved=True)
                .prefetch_related(
                    Prefetch(
                        "replies",
                        queryset=Comment.objects.filter(
                            is_approved=True,
                        ),
                    )
                )
                .order_by("-created_at")
            )
        else:
            raise NotFound("Course slug is required")


class CommentCreateAPIView(CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [LoginThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        course = get_object_or_404(Course, slug=self.kwargs["course_slug"])
        context["course"] = course
        parent_id = self.request.data.get("parent_id")
        if parent_id:
            parent_comment = get_object_or_404(
                Comment,
                id=parent_id,
                course=course,
            )
            context["parent_comment"] = parent_comment
        else:
            context["parent_comment"] = None

        return context


class EnrollCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)
        EnrollmentService.enroll(request.user, course)
        return Response(
            {"detail": "Enrolled successfully"},
            status=status.HTTP_201_CREATED,
        )


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

        course = get_object_or_404(Course, slug=course_slug)
        return Enrollment.objects.filter(course=course)


class ToggleLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, course_slug):
        course = get_object_or_404(Course, slug=course_slug)
        like = CourseLike.objects.filter(course=course, user=request.user).first()

        if like:
            like.delete()
            liked = False
        else:
            CourseLike.objects.create(course=course, user=request.user)
            liked = True

        return Response({"liked": liked, "likes_count": course.likes.count()})


class CompleteLessonAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        user = self.request.user

        ok, msg = ProgressService.complete_lessons(lesson, user)

        if not ok:
            return Response({"detail": msg}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": msg}, status=status.HTTP_200_OK)


class CourseProgressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_slug):

        course = get_object_or_404(Course, slug=course_slug)

        result = ProgressService.course_progress(course=course, user=request.user)

        if not result["ok"]:
            return Response(
                {"detail": result["message"]}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CourseProgressSerializer(result["data"])

        return Response(serializer.data)
