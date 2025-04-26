# backend/chat/urls.py
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    # Document endpoints
    path('documents/upload/', views.upload_document, name='upload_document'),
    path('documents/upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('documents/', views.list_documents, name='list_documents'),
    path('documents/set-active/', views.set_active_documents, name='set_active_documents'),
    path('documents/active/', views.get_active_documents, name='get_active_documents'),
    path('documents/<int:document_id>/', views.delete_document, name='delete_document'),
    
    # Chat endpoint
    path('chat/', views.chat, name='chat'),
    
    # Auth endpoints
    path('user/register/', views.CreateUserView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('token/verify/', TokenVerifyView.as_view(), name='verify_token'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # Background image endpoints
    path('backgrounds/upload/', views.upload_background, name='upload_background'),
    path('backgrounds/active/', views.get_active_background, name='get_active_background'),
    path('backgrounds/', views.list_backgrounds, name='list_backgrounds'),
    path('backgrounds/<int:background_id>/set-active/', views.set_active_background, name='set_active_background'),
    path('backgrounds/<int:background_id>/delete/', views.delete_background, name='delete_background'),
    
    # Simplified prompt endpoints
    path('prompts/', views.get_prompt, name='get_prompt'),
    path('prompts/update/', views.update_prompt, name='update_prompt'),
    
    # Settings endpoints
    path('settings/', views.get_settings, name='get_settings'),
    path('settings/update/', views.update_settings, name='update_settings'),
    
    # Public test endpoint
    path('public-test/', views.public_test, name='public_test'),
]