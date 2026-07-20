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

    class Meta:
        db_table = "accounts_user"

    def __str__(self):
        return self.username