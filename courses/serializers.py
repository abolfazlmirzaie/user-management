from rest_framework import serializers
from rest_framework.fields import ReadOnlyField
from users.models import Instructor
from .models import (
    Course,
    ContactUs,
    Category,
    Requirement,
    Comment,
    Lesson,
    Enrollment,
    Section,
)
from django.db.models import Count


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "video_url"]


# for normal users
class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "title", "lessons"]


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.CharField(source="instructor.user.full_name", read_only=True)
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField(default=False)
    sections = SectionSerializer(many=True, read_only=True)

    def get_is_liked(self, obj):
        user = self.context["request"].user
        return obj.likes.filter(user=user).exists()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "instructor",
            "level",
            "sections",
            "is_premium",
            "image",
            "likes_count",
            "is_liked",
        ]


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = ["course", "text"]


class CourseDetailSerializer(serializers.ModelSerializer):
    teacher = serializers.CharField(source="teacher.full_name")
    rating_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "instructor",
            "rating_count",
            "average_rating",
            "level",
            "is_premium",
            "image",
            "created_at",
            "description",
        ]


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUs
        fields = ["email", "phone", "address"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "title",
        ]


class CourseSerializerForCategory(serializers.RelatedField):
    def to_representation(self, value):
        return value.title

    def get_queryset(self):
        return Course.objects.all()


class CategoryDetailSerializer(serializers.ModelSerializer):
    courses = CourseSerializerForCategory(source="course", many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "title", "courses"]


class CommentSerializer(serializers.ModelSerializer):
    author = ReadOnlyField(source="author.username")
    replies = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ["author", "content", "created_at", "replies", "parent"]

    def get_replies(self, obj):
        replies = obj.replies.filter(is_approved=True)
        serializer = CommentSerializer(replies, many=True, context=self.context)
        return serializer.data

    def create(self, validated_data):
        request = self.context["request"]

        parent_comment = self.context.get("parent_comment")
        course = self.context["course"]

        return Comment.objects.create(
            author=request.user, parent=parent_comment, course=course, **validated_data
        )


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["user", "course"]
        read_only_fields = ["user", "course"]


class CourseProgressSerializer(serializers.ModelSerializer):
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    progress_percentage = serializers.IntegerField()


class SubmitRatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)


class InstructorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name")

    class Meta:
        model = Instructor
        fields = ["full_name", "avatar", "expertise"]


class InstructorInfoSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    full_name = serializers.CharField(source="user.full_name")
    courses = CourseSerializer(many=True, read_only=True)
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = Instructor
        fields = [
            "full_name",
            "email",
            "bio",
            "avatar",
            "expertise",
            "courses",
            "students_count",
        ]

    def get_students_count(self, obj):
        return (
            Enrollment.objects.filter(
                course__instructor=obj,
            )
            .values("user")
            .distinct()
            .count()
        )


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["title", "description", "image", "level", "is_premium"]


# for instructor
class SectionListCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["title"]
        read_only_fields = ["id"]


class LessonListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["title", "description", "video_url"]


class LessonUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "video_url", "order", "description"]
