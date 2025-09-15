from django.contrib import admin
from .models import BlogPost, Comment, Like

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display  = ("id", "title", "author", "category", "created_at", "is_active", "is_premium",)
    list_filter   = ("category", "created_at", "is_active", "is_premium",)
    search_fields = ("title", "body")
    raw_id_fields = ("author", "category")
    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'created_at')
    list_filter  = ('created_at',)
    search_fields = ('body',)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'user', 'created_at')
    list_filter  = ('created_at',)	