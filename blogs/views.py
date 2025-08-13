# blogs, views.py:
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from .models import BlogPost, Comment, Like
from .serializers import BlogPostSerializer, CommentSerializer, LikeSerializer
from drf_yasg import openapi

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    - Anyone can read (GET, HEAD, OPTIONS)
    - Only owner or staff can modify
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_staff
        )


@swagger_auto_schema(
    operation_summary="BlogPost endpoints",
    operation_description="Endpoints for managing blog posts"
)
class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.select_related("author", "category")
    serializer_class = BlogPostSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_summary="List all posts",
        operation_description="GET /api/v1/posts/",
        responses={200: BlogPostSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new post",
        operation_description="POST /api/v1/posts/",
        request_body=BlogPostSerializer,
        responses={201: BlogPostSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve single post",
        operation_description="GET /api/v1/posts/{id}/",
        responses={200: BlogPostSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update post (PUT)",
        operation_description="PUT /api/v1/posts/{id}/",
        request_body=BlogPostSerializer,
        responses={200: BlogPostSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update post (PATCH)",
        operation_description="PATCH /api/v1/posts/{id}/",
        request_body=BlogPostSerializer,
        responses={200: BlogPostSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete post",
        operation_description="DELETE /api/v1/posts/{id}/",
        responses={204: "Deleted successfully"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

"""
BlogPostViewSet endpoints:
    GET    /api/v1/posts/          - list posts
    POST   /api/v1/posts/          - create post
    GET    /api/v1/posts/{id}/     - retrieve post
    PUT    /api/v1/posts/{id}/     - full update post
    PATCH  /api/v1/posts/{id}/     - partial update post
    DELETE /api/v1/posts/{id}/     - delete post
"""

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    @swagger_auto_schema(
        operation_summary="List comments for a post",
        operation_description="GET /api/v1/posts/{post_pk}/comments/",
        responses={200: CommentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Add comment to post",
        operation_description="POST /api/v1/posts/{post_pk}/comments/",
        request_body=CommentSerializer,
        responses={201: CommentSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve single comment",
        operation_description="GET /api/v1/posts/{post_pk}/comments/{id}/",
        responses={200: CommentSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update comment (PUT)",
        operation_description="PUT /api/v1/posts/{post_pk}/comments/{id}/",
        request_body=CommentSerializer,
        responses={200: CommentSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partial update comment (PATCH)",
        operation_description="PATCH /api/v1/posts/{post_pk}/comments/{id}/",
        request_body=CommentSerializer,
        responses={200: CommentSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete comment",
        operation_description="DELETE /api/v1/posts/{post_pk}/comments/{id}/",
        responses={204: "Deleted successfully"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):        
        if getattr(self, 'swagger_fake_view', False): # if we're in schema generation mode            
            return Comment.objects.none()  # empty queryset during schema generation
        return Comment.objects.filter(post_id=self.kwargs['post_pk'])

    def perform_create(self, serializer):
        post = BlogPost.objects.get(pk=self.kwargs['post_pk'])
        serializer.save(author=self.request.user, post=post)

"""
CommentViewSet endpoints:
    GET    /api/v1/posts/{post_pk}/comments/        - list comments
    POST   /api/v1/posts/{post_pk}/comments/        - add comment
    GET    /api/v1/posts/{post_pk}/comments/{id}/   - single comment
    PUT    /api/v1/posts/{post_pk}/comments/{id}/   - full update
    PATCH  /api/v1/posts/{post_pk}/comments/{id}/   - partial update
    DELETE /api/v1/posts/{post_pk}/comments/{id}/   - delete comment
"""


class LikeViewSet(viewsets.ViewSet):
    """
    GET    /api/v1/posts/{post_pk}/likes/   - list likes
    POST   /api/v1/posts/{post_pk}/likes/   - toggle like
    """
    @swagger_auto_schema(
        operation_summary="List likes for a post",
        operation_description="GET /api/v1/posts/{post_pk}/likes/",
        responses={200: LikeSerializer(many=True)}
    )
    def list(self, request, post_pk=None):
        if getattr(self, 'swagger_fake_view', False):
            return Response([])
        likes = Like.objects.filter(post_id=post_pk)
        return Response(LikeSerializer(likes, many=True).data)

    @swagger_auto_schema(
    operation_summary="Toggle like on post",
    operation_description="POST /api/v1/posts/{post_pk}/likes/",
    responses={
        201: openapi.Response(
            description="Like created",
            examples={"application/json": {"liked": True}}
        ),
        200: openapi.Response(
            description="Like removed",
            examples={"application/json": {"liked": False}}
        )
    }
    )
    def create(self, request, post_pk=None):
        post = BlogPost.objects.get(pk=post_pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({'liked': False}, status=status.HTTP_200_OK)
        return Response({'liked': True}, status=status.HTTP_201_CREATED)


"""
crate post example
POST http://127.0.0.1:8000/api/v1/posts/ with bearer token
body:
{
    "title":"How i learned python",
    "body": "my python learning journey is a long way ...",
    "category":1
}

response:
201 Created
body:
{
    "id": 1,
    "title": "How i learned python",
    "body": "my python learning journey is a long way ...",
    "image": null,
    "video_url": "",
    "author": 2,
    "author_username": "anup",
    "category": 1,
    "category_name": "Programming",
    "created_at": "2025-08-13T15:15:22.648352Z",
    "updated_at": "2025-08-13T15:15:22.648352Z"
}
"""
