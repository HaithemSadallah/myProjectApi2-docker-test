from django.db import models
from django.utils.translation import gettext_lazy as _
from account.models import CustomUser

# Create your models here.


class Product(models.Model):
    name = models.CharField(max_length=200,default="",blank=True)
    description = models.TextField(max_length=1000,default="",blank=True)
    price = models.DecimalField(max_digits=7,decimal_places=2,default=0)
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    createAt = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name    
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, null=True)
    image = models.ImageField(_('Image'), upload_to='product_images/',null=True)
    createAt = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)