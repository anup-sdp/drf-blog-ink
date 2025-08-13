# users, models.py:

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField  # for image save in cloud

PHONE_REGEX = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)

def validate_image_size(image):
    max_kb = 500
    if image and image.size > max_kb * 1024:
        raise ValidationError(f"Image file too large ( > {max_kb}KB )")

class CustomUser(AbstractUser):
    is_active = models.BooleanField(default=False) # activate by email, djoser
    phone_number = models.CharField(max_length=20, validators=[PHONE_REGEX], blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, help_text="City or location (e.g., Dhaka)")
    bio = models.TextField(blank=True, max_length=500)
    #profile_picture = models.ImageField(upload_to='blog-ink_avatars/', validators=[validate_image_size], blank=True, null=True) # latter use claudinary field
    profile_picture = CloudinaryField('image', folder='blog-ink_avatars', blank=True, null=True,)  # to save image in cloud, default='blog-ink_avatars/default_img.png'
    
    def save(self, *args, **kwargs):
        if not self.pk:  # only for new users
            self.is_active = False  # set True by activation email.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username