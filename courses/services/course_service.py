from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from courses.models import Enrollment, LessonProgress, Lesson


class ProgressService:
    @staticmethod
    def complete_lessons(lesson, user):
        enrollment = Enrollment.objects.filter(
            user=user,
            course=lesson.section.course,
        ).first()
        if not enrollment:
            return False, "you are not enrolled in this course"
        progress = LessonProgress.objects.create(
            enrollment=enrollment,
            lesson=lesson,
        )
        if progress.is_complete:
            return False, "already complete"

        progress.is_complete = True
        progress.completed_at = timezone.now()
        progress.save()

        return True, "mark as completed"

    @staticmethod
    def course_progress(course, user):
        enrollment = Enrollment.objects.filter(
            user=user,
            course=course,
        ).first()

        if not enrollment:
            return {
                "ok": False,
                "message": "you are not enrolled in this course",
                "data": None,
            }

        total_lessons = Lesson.objects.filter(
            section__course=course,
        ).count()

        completed_lessons = LessonProgress.objects.filter(
            enrollment=enrollment,
            is_complete=True,
        ).count()

        progress_percentage = (
            (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        )

        return {
            "ok": True,
            "data": {
                "total_lessons": total_lessons,
                "completed_lessons": completed_lessons,
                "progress_percentage": progress_percentage,
            },
        }
