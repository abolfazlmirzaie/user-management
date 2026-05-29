from django.contrib import admin
from .models import Course, Category, Comment, Section, Lesson, Requirement, ContactUs



class CategoryInline(admin.TabularInline):
    model = Category.course.through
    extra = 1




class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1





class RequirementInline(admin.TabularInline):
    model = Requirement
    extra = 1
    fields = ('text',)


class SectionInline(admin.TabularInline):
    model = Section
    extra = 2

    inlines = [LessonInline]



@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "teacher", "level", "is_premium")
    list_filter = ("level", "is_premium")
    search_fields = ("title", "teacher__first_name", "teacher__last_name")
    inlines = [CategoryInline, RequirementInline, SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course")
    search_fields = ("title", "course__title")
    inlines = [LessonInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    search_fields = ("title",)



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("course", "author", "parent", "content", "is_approved")
    search_fields = ("course__title", "author__username")



admin.site.register(ContactUs)
