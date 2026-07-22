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
    
class Role(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100,)
    description = models.TextField(blank=True,)
    is_active = models.BooleanField(default=True,)
    created_at = models.DateTimeField(auto_now_add=True,)
    updated_at = models.DateTimeField(auto_now=True,)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    
