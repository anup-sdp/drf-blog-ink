# users, signals.py:
# delete profile avatar image on user delete or avatar update.

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from cloudinary.uploader import destroy
from .models import CustomUser


@receiver(post_delete, sender=CustomUser)
def delete_avatar_on_user_delete(sender, instance, **kwargs):
    """Remove Cloudinary avatar when the user is deleted."""
    if instance.profile_picture:
        destroy(instance.profile_picture.public_id)


@receiver(pre_save, sender=CustomUser)
def delete_old_avatar_on_avatar_update(sender, instance, **kwargs):
    """Remove the previous Cloudinary avatar when the field is replaced."""
    if not instance.pk: # new user
        return

    try:
        old_user = CustomUser.objects.get(pk=instance.pk)
    except CustomUser.DoesNotExist:
        return

    old_pic = old_user.profile_picture
    new_pic = instance.profile_picture

    if old_pic and old_pic != new_pic:
        destroy(old_pic.public_id)		