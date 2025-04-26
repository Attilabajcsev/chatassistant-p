# backend/chat/views.py
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Document, Conversation, BackgroundImage, Prompt, Settings
from .serializers import UserSerializer
from .utils import error_response, success_response
from .services import (
    RAGService, DocumentProcessingService, 
    BackgroundService, DocumentService, 
    PromptService, SettingsService
)

logger = logging.getLogger(__name__)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

@csrf_exempt
@require_http_methods(["POST"])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document(request):
    """
    API endpoint to upload a document and generate its embedding
    
    Accepts JSON data with:
    - title: Optional document title
    - content: Document text content
    - source: Optional source information
    """
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        if 'content' not in data:
            return error_response('Missing required field: content', status=400)

        document = Document.objects.create(
            title=data.get('title', ''),
            content=data['content'],
            source=data.get('source', ''),
            user=request.user
        )
        
        # Generate and store embedding
        try:
            embedding_service = DocumentProcessingService().embedding_service
            document = embedding_service.process_document(document)
            
            return success_response(
                {'document_id': document.id},
                'Document uploaded and processed successfully'
            )
        except Exception as e:
            # If embedding fails, delete the document and return error
            logger.error(f"Error processing document: {str(e)}")
            document.delete()
            raise
            
    except json.JSONDecodeError:
        return error_response('Invalid JSON data', status=400)
    except Exception as e:
        return error_response(str(e), status=500, exc=e)

@csrf_exempt
@require_http_methods(["POST"])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    API endpoint for chat interaction with RAG
    
    Accepts JSON data with:
    - message: User's message/query
    - conversation_id: Optional ID to continue existing conversation
    """
    try:
        data = json.loads(request.body)
        
        if 'message' not in data:
            return error_response('Missing required field: message', status=400)
            
        message = data['message']
        conversation_id = data.get('conversation_id')

        # Use RAG service to process the query
        rag_service = RAGService()
        response, relevant_documents = rag_service.process_query(
            message, 
            conversation_id, 
            user=request.user  
        )
        
        if not conversation_id:
            conversation = Conversation.objects.filter(
                user=request.user
            ).latest('created_at')
            conversation_id = conversation.session_id

        # Format source information for the response
        sources = []
        for doc in relevant_documents:
            sources.append({
                'id': doc.id,
                'title': doc.title,
                'content_preview': doc.content[:100] + '...' if len(doc.content) > 100 else doc.content
            })
        
        return success_response({
            'response': response,
            'conversation_id': conversation_id,
            'sources': sources
        })
        
    except json.JSONDecodeError:
        return error_response('Invalid JSON data', status=400)
    except Exception as e:
        return error_response(str(e), status=500, exc=e)

@csrf_exempt
@require_http_methods(["POST"])
@api_view(['POST']) 
@permission_classes([IsAuthenticated])
def upload_pdf(request):
    """
    API endpoint to upload and process a PDF document
    
    Expects multipart/form-data with:
    - pdf_file: The PDF file
    - title: Optional title for the document
    """
    try:
        if 'pdf_file' not in request.FILES:
            return error_response('No PDF file provided', status=400)
        
        pdf_file = request.FILES['pdf_file']
        title = request.POST.get('title', pdf_file.name)
        
        # Process the PDF using the service
        processing_service = DocumentProcessingService()
        documents = processing_service.process_pdf(pdf_file, title, user=request.user)
        
        return success_response({
            'document_count': len(documents),
            'title': title
        }, f'PDF processed successfully into {len(documents)} chunks')
        
    except Exception as e:
        return error_response(str(e), status=500, exc=e)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_background(request):
    """
    API endpoint to upload and save a background image
    """
    try:
        if 'background_image' not in request.FILES:
            return error_response('No image file provided', status=400)
        
        background_file = request.FILES['background_image']
        name = request.POST.get('name', background_file.name)
        is_active = request.POST.get('is_active', 'false').lower() == 'true'
        
        # Use the service to create the background
        background = BackgroundService.create_background(
            name, 
            background_file, 
            is_active, 
            request.user
        )
        
        # Return success response with image URL
        return success_response({
            'background_id': background.id,
            'image_url': request.build_absolute_uri(background.image.url) if hasattr(background.image, 'url') else None,
            'is_active': background.is_active
        }, 'Background image uploaded successfully')
        
    except Exception as e:
        return error_response(f"Error uploading background: {str(e)}", status=500, exc=e)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_background(request):
    """
    API endpoint to get the currently active background image
    """
    try:
        active_background = BackgroundService.get_active_background(request.user)
        
        if active_background:
            return success_response({
                'background_id': active_background.id,
                'name': active_background.name,
                'image_url': request.build_absolute_uri(active_background.image.url) if hasattr(active_background.image, 'url') else None
            })
        else:
            return success_response({
                'message': 'No active background found',
                'image_url': None
            })
            
    except Exception as e:
        return error_response(f"Error getting active background: {str(e)}", status=500, exc=e)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_backgrounds(request):
    """
    API endpoint to list all available background images for the current user
    """
    try:
        backgrounds = BackgroundService.list_backgrounds(request.user)

        background_list = [{
            'id': bg.id,
            'name': bg.name,
            'image_url': request.build_absolute_uri(bg.image.url) if hasattr(bg.image, 'url') else None,
            'is_active': bg.is_active,
            'created_at': bg.created_at
        } for bg in backgrounds]
        
        return success_response({'backgrounds': background_list})
            
    except Exception as e:
        return error_response(f"Error listing backgrounds: {str(e)}", status=500, exc=e)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def set_active_background(request, background_id):
    """
    API endpoint to set a specific background as active
    """
    try:
        background = BackgroundService.set_active_background(background_id, request.user)
        
        return success_response({
            'background_id': background.id
        }, f'Background "{background.name}" set as active')
            
    except BackgroundImage.DoesNotExist:
        return error_response(f'Background with ID {background_id} not found', status=404)
    except Exception as e:
        return error_response(f"Error setting active background: {str(e)}", status=500, exc=e)

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_background(request, background_id):
    """
    API endpoint to delete a specific background image
    """
    try:
        # Try to get the name first for the success message
        background = BackgroundImage.objects.get(id=background_id, user=request.user)
        background_name = background.name
        
        # Use the service to delete the background
        BackgroundService.delete_background(background_id, request.user)
        
        return success_response({}, f'Background "{background_name}" deleted successfully')
            
    except BackgroundImage.DoesNotExist:
        return error_response(f'Background with ID {background_id} not found', status=404)
    except Exception as e:
        return error_response(f"Error deleting background: {str(e)}", status=500, exc=e)
    
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """
    API endpoint to list all documents for the current user
    """
    try:
        documents = DocumentService.list_documents(request.user)
        
        # Format the documents for the response
        documents_data = [{
            'id': doc.id,
            'title': doc.title,
            'source': doc.source,
            'created_at': doc.created_at.isoformat(),
            'is_active': doc.is_active
        } for doc in documents]
        
        return success_response({'documents': documents_data})
        
    except Exception as e:
        return error_response(str(e), status=500, exc=e)

@csrf_exempt
@require_http_methods(["POST"])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_active_documents(request):
    """
    API endpoint to set specific documents as active for RAG
    
    Expects JSON data with:
    - document_ids: List of document IDs to set as active
    """
    try:
        data = json.loads(request.body)
        
        if 'document_ids' not in data:
            return error_response('Missing required field: document_ids', status=400)
            
        document_ids = data['document_ids']
        
        # Use the service to set active documents
        updated = DocumentService.set_active_documents(document_ids, request.user)
        
        if not updated and document_ids:
            return error_response('No documents were activated. Make sure the documents belong to you.', status=400)
        
        return success_response({}, 'Documents set as active successfully')
        
    except json.JSONDecodeError:
        return error_response('Invalid JSON data', status=400)
    except Exception as e:
        return error_response(str(e), status=500, exc=e)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_documents(request):
    """
    API endpoint to get the currently active documents for the authenticated user
    """
    try:
        active_docs = DocumentService.get_active_documents(request.user)
        
        # Format the documents for the response
        active_docs_data = [{
            'id': doc.id,
            'title': doc.title,
            'source': doc.source,
            'created_at': doc.created_at.isoformat()
        } for doc in active_docs]
        
        return success_response({'active_documents': active_docs_data})
        
    except Exception as e:
        return error_response(str(e), status=500, exc=e)

@csrf_exempt
@api_view(['DELETE'])  
@permission_classes([IsAuthenticated]) 
def delete_document(request, document_id):
    """
    API endpoint to delete a specific document or all documents with the same source
    """
    try:
        # Get the document source for the success message
        document = Document.objects.get(id=document_id, user=request.user)
        source = document.source
        
        # Use the service to delete the document
        deleted_count = DocumentService.delete_document(document_id, request.user)
        
        return success_response({}, f'Successfully deleted all chunks of "{source}" ({deleted_count} documents)')
            
    except Document.DoesNotExist:
        return error_response(f'Document with ID {document_id} not found', status=404)
    except Exception as e:
        return error_response(f"Error deleting document: {str(e)}", status=500, exc=e)
    
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_prompt(request):
    """
    API endpoint to get the user's prompt
    """
    try:
        # Use the service to get prompt
        prompt = PromptService.get_prompt(request.user)
        
        if prompt:
            return success_response({
                'prompt': {
                    'id': prompt.id,
                    'name': prompt.name,
                    'assistant_role': prompt.assistant_role,
                    'website_context': prompt.website_context,
                    'knowledge_context': prompt.knowledge_context,
                    'response_guidelines': prompt.response_guidelines,
                    'restrictions': prompt.restrictions,
                    'created_at': prompt.created_at.isoformat() if prompt.created_at else None
                }
            })
        else:
            return success_response({
                'message': 'No prompt found',
                'prompt': None
            })
            
    except Exception as e:
        return error_response(str(e), status=500, exc=e)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_prompt(request):
    """
    API endpoint to update the user's prompt
    """
    try:
        data = json.loads(request.body)
        
        # Use the service to update prompt
        PromptService.update_prompt(data, request.user)
        
        return success_response({}, 'Prompt updated successfully')
        
    except json.JSONDecodeError:
        return error_response('Invalid JSON data', status=400)
    except Exception as e:
        return error_response(f"Error updating prompt: {str(e)}", status=500, exc=e)

@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_settings(request):
    """
    API endpoint to get the current active settings
    """
    try:
        # Use the service to get settings
        settings = SettingsService.get_settings(request.user)
        
        # Convert to dictionary
        settings_data = {
            'id': settings.id,
            'chatName': settings.chatName,
            'colorPrimary': settings.colorPrimary,
            'buttonBg': settings.buttonBg,
            'welcomeMessage': settings.welcomeMessage,
            'disclaimerTitle': settings.disclaimerTitle,
            'disclaimerIntro': settings.disclaimerIntro,
            'disclaimerPoints': settings.disclaimerPoints,
            'acceptButtonText': settings.acceptButtonText,
            'sendButtonText': settings.sendButtonText,
            'footerDisclaimer': settings.footerDisclaimer,
            'privacyPolicyText': settings.privacyPolicyText,
            'is_active': settings.is_active,
            'created_at': settings.created_at.isoformat() if settings.created_at else None,
            'updated_at': settings.updated_at.isoformat() if settings.updated_at else None
        }
        
        return JsonResponse(settings_data)
            
    except Exception as e:
        return error_response(f"Error getting settings: {str(e)}", status=500, exc=e)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_settings(request):
    """
    API endpoint to update settings
    """
    try:
        data = json.loads(request.body)
        
        # Use the service to update settings
        SettingsService.update_settings(data, request.user)
        
        return success_response({}, 'Settings updated successfully')
        
    except json.JSONDecodeError:
        return error_response('Invalid JSON data', status=400)
    except Exception as e:
        return error_response(f"Error updating settings: {str(e)}", status=500, exc=e)

class LogoutView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                
            response = Response({"detail": "Successfully logged out."})
            response.delete_cookie('access')
            response.delete_cookie('refresh')
            return response
        except Exception as e:
            return error_response(f"Error logging out: {str(e)}", status=400)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def public_test(request):
    """Public test endpoint to verify CORS is working"""
    
    if request.method == 'POST':
        data = request.data
    else:
        data = {}
    
    return success_response({
        'message': 'Public API endpoint works!',
        'method': request.method,
        'received_data': data,
        'cors_working': True
    })

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])  
def user_profile(request):
    """
    API endpoint to get or update user profile information
    """
    if not request.user.is_authenticated:
        return error_response('Authentication required', status=401)
    
    user = request.user
    
    if request.method == 'GET':
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined,
            'last_login': user.last_login
        }
        return JsonResponse(data)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            
            if 'email' in data:
                user.email = data['email']
            
            user.save()
            
            return success_response({}, 'Profile updated successfully')
            
        except Exception as e:
            return error_response(f"Error updating profile: {str(e)}", status=400, exc=e)