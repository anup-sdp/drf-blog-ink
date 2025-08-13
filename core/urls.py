from rest_framework.routers import DefaultRouter  # use nested router ? ----------------
from rest_framework_nested import routers as nested
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path, include, re_path
from users.views import CustomUserViewSet
from categories.views import CategoryViewSet
from blogs.views import BlogPostViewSet, CommentViewSet, LikeViewSet
from payment.views import PaymentPlaceholderViewSet

# do as, https://github.com/anup-sdp/sdp-drf-library_mgmt/blob/main/library_management/urls.py ------- follow 
router = DefaultRouter()
router.register('users', CustomUserViewSet)  # /api/v1/users/
router.register('categories', CategoryViewSet)  # GET /api/v1/categories/ – public list, POST /api/v1/categories/ – staff only
router.register('posts', BlogPostViewSet)  # /api/v1/posts/
router.register('payments', PaymentPlaceholderViewSet, basename='payment')  # GET /api/v1/payments/

# nested under /posts/
posts_router = nested.NestedDefaultRouter(router, 'posts', lookup='post')
posts_router.register('comments', CommentViewSet, basename='post-comments')
posts_router.register('likes', LikeViewSet, basename='post-likes')    
    
schema_view = get_schema_view(
   openapi.Info(
      title="blog-ink (phibook) API",
      default_version='v1',
      description="API documentation for the blog-ink (phiBook) blog app",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@library.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,  # allows public access to the schema
   permission_classes=(permissions.AllowAny,),  # allows anyone to access the docs   
)

urlpatterns = [    
	path('', include(router.urls)),
    path('', include(posts_router.urls)), 
    # JWT endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # POST request to get access/refresh tokens
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
	# djoser endpoints
    path('auth/', include('djoser.urls')),  # auth/users, auth/users/me 	
    path('auth/', include('djoser.urls.jwt')),  # Using Djoser's JWT integration    
	#	
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # /api/v1/swagger/
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # /api/v1/redoc/
]

"""
nested:
/api/v1/posts/	GET/POST	list/create posts
/api/v1/posts/{id}/	GET/PATCH/PUT/DELETE	retrieve/edit/delete post
/api/v1/posts/{id}/comments/	GET/POST	list/add comments for post
/api/v1/posts/{id}/comments/{id}/	GET/PATCH/DELETE	edit/delete single comment
/api/v1/posts/{id}/likes/	GET	list likes
/api/v1/posts/{id}/likes/	POST	create (or remove) current user's like
"""