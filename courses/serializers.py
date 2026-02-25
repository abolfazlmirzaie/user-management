from rest_framework import serializers
from . models import Course


class CourseSerializer(serializers.ModelSerializer):
    total_duration = serializers.SerializerMethodField()
    teacher = serializers.CharField(source="teacher.full_name")

    def get_total_duration(self, obj):
        from .services.course_service import CourseService
        return CourseService.get_total_duration(obj.id)
    class Meta:
        model = Course
        fields =["id", "title", "teacher", "level", "total_duration", "is_premium", "image"]