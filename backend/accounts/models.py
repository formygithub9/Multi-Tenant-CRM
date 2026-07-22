from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True,blank=True,)
    objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.email})"
    

    
    
