from django.db import models
from users.models import CustomUser
from autoslug import AutoSlugField
from moviepy import VideoFileClip


class Course(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="courses"
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

    def __str__(self):
        return self.title


class Section(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    lesson_number = models.PositiveIntegerField(default=1)
    duration_hour = models.PositiveIntegerField(default=0)
    duration_minute = models.PositiveIntegerField(default=0)
    duration_second = models.PositiveIntegerField(default=0)
    video = models.FileField(upload_to="courses/lessons/video", blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.video:
            clip = VideoFileClip(self.video.path)
            total_seconds = int(clip.duration)
            clip.close()

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60

            self.duration_hour = hours
            self.duration_minute = minutes
            self.duration_second = seconds

            super().save(
                update_fields=["duration_hour", "duration_minute", "duration_second"]
            )

    @property
    def duration(self):
        if self.duration_hour == 0:
            return f"{self.duration_minute}:{self.duration_second:02d}"

        return f"{self.duration_hour}:{self.duration_minute:02d}:{self.duration_second:02d}"

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

    def get_parent_comments(self):
        return Comment.objects.filter(parent=None)


class Requirement(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="requirements"
    )
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
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="enrollment"
    )
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name="students"
    )
    enrollment_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"
