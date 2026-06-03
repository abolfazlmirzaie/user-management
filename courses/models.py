from django.db import models
from users.models import CustomUser, Instructor
from autoslug import AutoSlugField


class Course(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    instructor = models.ForeignKey(
        Instructor, on_delete=models.CASCADE, related_name="courses"
    )
    image = models.ImageField(upload_to="courses/image", blank=True)
    LEVEL_CHOICES = [
        ("beginner", "Beginner"),
        ("medium", "Medium"),
        ("advance", "Advance"),
    ]

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="beginner")
    is_premium = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = AutoSlugField(max_length=150, unique=True, populate_from="title")

    @property
    def like_count(self):
        return self.likes.count()

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    video_url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order",)

    def __str__(self):
        return self.title


class Comment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.author.username} - {self.course.title}"


class Requirement(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="requirements"
    )
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Category(models.Model):
    course = models.ManyToManyField(Course, related_name="categories")
    title = models.CharField(max_length=150)
    slug = AutoSlugField(populate_from="title", unique=True)

    def __str__(self):
        return self.title


class ContactUs(models.Model):
    email = models.EmailField()
    phone = models.CharField(max_length=11)
    address = models.CharField(max_length=120)

    def __str__(self):
        return self.email


class Enrollment(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="enrollment"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="students"
    )
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_enrollment",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"


class CourseLike(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="liked_course"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "user")


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="lesson_progress"
    )
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="progress"
    )
    is_complete = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"],
                name="unique_lesson_progress",
            )
        ]
