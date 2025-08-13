# delete BlogPost image when needed  (if post deleted or image updated)
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from cloudinary.uploader import destroy
from .models import BlogPost


@receiver(post_delete, sender=BlogPost)
def delete_post_image_on_post_delete(sender, instance, **kwargs):
    """Remove Cloudinary image when the whole post is deleted."""
    if instance.image:
        destroy(instance.image.public_id)


@receiver(pre_save, sender=BlogPost)
def delete_old_image_on_image_update(sender, instance, **kwargs):
    """Remove the previous Cloudinary image when the image field is replaced."""
    if not instance.pk: # new post 
        return

    try:
        old_post = BlogPost.objects.get(pk=instance.pk)
    except BlogPost.DoesNotExist:
        return

    old_image = old_post.image
    new_image = instance.image

    # image changed (old exists and is different)
    if old_image and old_image != new_image:
        destroy(old_image.public_id)