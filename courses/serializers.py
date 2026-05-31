from rest_framework import serializers
from rest_framework.fields import ReadOnlyField

from .models import (
    Course,
    ContactUs,
    Category,
    Requirement,
    Comment,
    Lesson,
    Enrollment,
    CourseLike,
)


class CourseSerializer(serializers.ModelSerializer):
    total_duration = serializers.SerializerMethodField()
    teacher = serializers.CharField(source="instructor.user.full_name")
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()

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
            "total_duration",
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

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "instructor",
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


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "lesson_number", "duration", "video"]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["user", "course"]
        read_only_fields = ["user", "course"]
