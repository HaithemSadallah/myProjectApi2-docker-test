from django.db import models
from django.contrib.auth.models import *
from django.dispatch import receiver 
from django.db.models.signals import post_save
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255,default="")
    phone_number=models.CharField(max_length=10,default="")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name


class Profile(models.Model):
    user=models.OneToOneField(CustomUser,related_name='profile',on_delete=models.CASCADE)
    reset_password_token=models.CharField(max_length=150,default="",blank=True)
    reset_password_expire=models.DateTimeField(null=True,blank=True)  


  
@receiver(post_save, sender=CustomUser)
def save_profile(sender,instance, created, **kwargs):
    print('instance',instance)
    user = instance

    if created:
            profile = Profile(user = user)
            profile.save()   