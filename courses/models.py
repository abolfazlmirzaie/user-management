from django.db import models
from users.models import CustomUser
from autoslug import AutoSlugField


class Course(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="courses")
    image = models.ImageField(upload_to="courses/", blank=True)
    level = models.CharField(max_length=50, default="beginner")
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = AutoSlugField(max_length=150, unique=True, populate_from="title")

    def __str__(self):
        return self.title



class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=1)


    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    lesson_number = models.PositiveIntegerField(default=1)
    duration_minute = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author.username} - {self.course.title}"


class Requirement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="requirements")
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class TeacherProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="teachers/", blank=True)
    social_links = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    course = models.ManyToManyField(Course,  related_name="categories")
    title = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from="title", unique=True)

    def __str__(self):
        return self.title