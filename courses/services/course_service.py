from django.db.models import F, ExpressionWrapper, IntegerField, Sum

class CourseService:
    @staticmethod
    def get_total_duration(course_id: int) -> str:
        from courses.models import Course

        total_seconds = (
            Course.objects.filter(id=course_id)
            .annotate(
                total_seconds=Sum(
                    ExpressionWrapper(
                        F("sections__lessons__duration_hour") * 3600
                        + F("sections__lessons__duration_minute") * 60
                        + F("sections__lessons__duration_second"),
                        output_field=IntegerField(),
                    )
                )
            )
            .values_list("total_seconds", flat=True)
            .first()
            or 0
        )

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        if hours == 0:
            return f"{minutes}:{seconds:02d}"

        return f"{hours}:{minutes:02d}:{seconds:02d}"