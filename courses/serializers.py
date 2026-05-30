from rest_framework import serializers
from rest_framework.fields import ReadOnlyField

from .models import (
    Course,
    ContactUs,
    Category,
    Requirement,
    Comment,
    Lesson,
    Enrollment, CourseLike,
)


class CourseSerializer(serializers.ModelSerializer):
    total_duration = serializers.SerializerMethodField()
    teacher = serializers.CharField(source="teacher.full_name")
    likes_count = serializers.IntegerField(source="likes.count", read_only=True)
    is_liked = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        user = self.context["request"].user
        return obj.likes.filter(user=user).exists()


    def get_total_duration(self, obj):
        from .services.course_service import CourseService

        return CourseService.get_total_duration(obj.id)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "teacher",
            "level",
            "total_duration",
            "is_premium",
            "image",
            'likes_count',
            'is_liked'
        ]


class RequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirement
        fields = ["course", "text"]


class CourseDetailSerializer(serializers.ModelSerializer):
    total_duration = serializers.SerializerMethodField()
    teacher = serializers.CharField(source="teacher.full_name")

    # requirement = serializers.SerializerMethodField(RequirementSerializer)
    def get_total_duration(self, obj):
        from .services.course_service import CourseService

        return CourseService.get_total_duration(obj.id)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "teacher",
            "level",
            "total_duration",
            "is_premium",
            "image",
            "created_at",
            "description",
            "price",
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
    user = ReadOnlyField(source="user.username")
    replise = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["user", "course", "parent", "content", "created_at", "replise"]

    def get_replise(self, obj):
        replies = obj.replies.filter(is_approved=True)
        serializer = CommentSerializer(replies, many=True)
        return serializer.data

    def create(self, validated_data):
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("request context is missing")

        parent_id = self.context.get("parent_id")

        comment = Comment.objects.create(
            user=request.user,
            parent=parent_id,
            content=validated_data[self.context.get("content")],
            **validated_data,
        )
        return comment


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "lesson_number", "duration", "video"]


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ["user", "course"]
        read_only_fields = ["user", "course"]
