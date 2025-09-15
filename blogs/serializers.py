from rest_framework import serializers
from .models import BlogPost, Comment, Like
from cloudinary.models import CloudinaryField

MAX_IMAGE_KB = 2 * 1024  # 2 MB

class BlogPostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source="author.username", read_only=True)
    category_name   = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model  = BlogPost
        fields = [
            "id", "title", "body", "image", "video_url",
            "author", "author_username", "category", "category_name",
            "created_at", "updated_at", "is_active", "is_premium"
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def validate_image(self, value):
        if value and value.size > MAX_IMAGE_KB * 1024:
            raise serializers.ValidationError(f"Image must be ≤ {MAX_IMAGE_KB} KB.")
        return value
    
    
class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_username', 'body', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class LikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'post', 'user', 'username', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']	