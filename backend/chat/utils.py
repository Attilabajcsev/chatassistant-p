# backend/chat/utils.py
from django.http import JsonResponse
import logging
import traceback

logger = logging.getLogger(__name__)

def error_response(message, status=400, log_error=True, exc=None):
    """
    Create a consistent error response
    
    Args:
        message: Error message to return to client
        status: HTTP status code
        log_error: Whether to log the error (default: True)
        exc: Exception object if available
        
    Returns:
        JsonResponse with consistent error format
    """
    if log_error:
        if exc:
            logger.error(f"{message}: {str(exc)}")
            logger.debug(traceback.format_exc())
        else:
            logger.error(message)
    
    return JsonResponse({
        'status': 'error',
        'message': message
    }, status=status)


def success_response(data=None, message=None, status=200):
    """
    Create a consistent success response
    
    Args:
        data: Optional data to include in response
        message: Optional success message
        status: HTTP status code
        
    Returns:
        JsonResponse with consistent success format
    """
    response = {
        'status': 'success'
    }
    
    if message:
        response['message'] = message
        
    if data:
        # If data is a dict, merge it with the response
        if isinstance(data, dict):
            for key, value in data.items():
                response[key] = value
        else:
            # Otherwise set it as 'data' field
            response['data'] = data
    
    return JsonResponse(response, status=status)