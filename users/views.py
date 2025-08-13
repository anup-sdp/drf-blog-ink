from rest_framework import viewsets, permissions
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import CustomUser
from .serializers import CustomUserSerializer

class IsStaffOrReadOnlyForAuthenticated(permissions.BasePermission):
    """
    • Authenticated users can list / retrieve.
    • Only staff/superuser can create / update / destroy.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff

@swagger_auto_schema(
    tags=['Users'],
    operation_description="API endpoint for managing users in the system. "
                         "Authenticated users can list and view active users. "
                         "Staff users have full CRUD access to all users."
)
class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsStaffOrReadOnlyForAuthenticated]
    
    @swagger_auto_schema(
        operation_summary="List users",
        operation_description="Returns a list of users. Non-staff users only see active users.",
        responses={200: CustomUserSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Create a user",
        operation_description="Create a new user. Staff access only.",
        request_body=CustomUserSerializer,
        responses={201: CustomUserSerializer}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Retrieve a user",
        operation_description="Get details of a specific user.",
        responses={200: CustomUserSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Update a user",
        operation_description="Update a user's details. Staff access only.",
        request_body=CustomUserSerializer,
        responses={200: CustomUserSerializer}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Partial update a user",
        operation_description="Partially update a user's details. Staff access only.",
        request_body=CustomUserSerializer,
        responses={200: CustomUserSerializer}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(
        operation_summary="Delete a user",
        operation_description="Delete a user. Staff access only.",
        responses={204: "No content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(is_active=True)  # filter out inactive users for non-staff