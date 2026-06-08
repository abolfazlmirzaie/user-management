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
    Section,
)


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "video_url"]


class SectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = ["id", "title", "lessons"]


class CourseSerializer(serializers.ModelSerializer):
    teacher = serializers.CharField(source="instructor.user.full_name")
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()
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
