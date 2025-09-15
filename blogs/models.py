from django.db import models
from django.conf import settings
from categories.models import Category
from cloudinary.models import CloudinaryField


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()
    image = CloudinaryField("image", folder="blog-ink_post_image", blank=True, null=True) # --- image
    video_url = models.URLField(blank=True, help_text="Optional YouTube URL")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="posts", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True) #
    is_premium = models.BooleanField(default=False) # 
    category = models.ForeignKey(Category,related_name="posts",on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title   
    


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE) # who commented
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} on {self.post.title}"


class Like(models.Model):
    post = models.ForeignKey(BlogPost, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('post', 'user')  # one like per user per post

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"