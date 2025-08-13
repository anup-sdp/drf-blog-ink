from rest_framework import viewsets, permissions
from .models import Category
from .serializers import CategorySerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]
    
    @swagger_auto_schema(
        operation_summary="List all categories",
        operation_description="GET /api/v1/categories/",
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create a new category",
        operation_description="POST /api/v1/categories/ (Staff only)",
        request_body=CategorySerializer,
        responses={
            201: CategorySerializer,
            403: "Permission denied - only staff can create categories"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Retrieve a specific category",
        operation_description="GET /api/v1/categories/{id}/",
        responses={200: CategorySerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update a category (PUT)",
        operation_description="PUT /api/v1/categories/{id}/ (Staff only)",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            403: "Permission denied - only staff can update categories"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partially update a category (PATCH)",
        operation_description="PATCH /api/v1/categories/{id}/ (Staff only)",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            403: "Permission denied - only staff can update categories"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete a category",
        operation_description="DELETE /api/v1/categories/{id}/ (Staff only)",
        responses={
            204: "Category deleted successfully",
            403: "Permission denied - only staff can delete categories"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
"""
Category endpoints:
- List all categories (any authenticated)
- Create new category (staff only)
- Retrieve specific category (any authenticated)
- Update category (staff only)
- Delete category (staff only)
"""	


"""
example: with bearer token,
POST http://127.0.0.1:8000/api/v1/categories/
body:
{
    "name":"Programming",
    "description":"blogs about programming"
}

response:
201 Created
{
    "id": 1,
    "name": "Programming",
    "description": "blogs about programming",
    "created_at": "2025-08-13T14:24:29.731060Z"
}

"""