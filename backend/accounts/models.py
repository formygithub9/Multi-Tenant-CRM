from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


# Create your models here.
class User(AbstractUser):
    """
    Custom User model.
    """

    email = models.EmailField(unique=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.email})"
    
