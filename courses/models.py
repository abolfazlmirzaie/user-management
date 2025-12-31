from django.db import models

from users.models import CustomUser


# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=100)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField()
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.title
