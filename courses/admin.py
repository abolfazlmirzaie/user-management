from django.contrib import admin
from .models import Course, Category, Comment, Section, Lesson, Requirement


class CategoryInline(admin.TabularInline):
    model = Category.course.through
    extra = 1

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "level", "is_premium")
    list_filter = ("level", "is_premium")
    search_fields = ("title", "teacher__first_name", "teacher__last_name")
    inlines = [CategoryInline, SectionInline]

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    search_fields = ("title",)
    inlines = [LessonInline]

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title",)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "duration_minute", "duration")
    search_fields = ("title",)

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ("text", "course")