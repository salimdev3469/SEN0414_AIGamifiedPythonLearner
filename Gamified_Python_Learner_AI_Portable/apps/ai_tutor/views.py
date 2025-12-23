from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from .utils import get_chatbot
from .models import ChatConversation


@login_required
@require_http_methods(["POST"])
def send_message_view(request):
    """
    Send a message to the chatbot and get a response.
    
    POST data:
        - message: User's message
        - context_type: optional (general/lesson/exercise)
        - context_id: optional (ID of lesson or exercise)
        - code_snippet: optional (code to debug)
        - conversation_id: optional (existing conversation ID)
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        context_type = data.get('context_type', 'general')
        context_id = data.get('context_id')
        code_snippet = data.get('code_snippet')
        
        # Get chatbot instance
        chatbot = get_chatbot()
        
        # Send message and get response
        result = chatbot.send_message(
            user=request.user,
            message_content=message,
            context_type=context_type,
            context_id=context_id,
            code_snippet=code_snippet
        )
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in send_message_view: {e}")
        print(f"Traceback: {error_details}")
        
        # Return more detailed error in development
        error_message = str(e) if settings.DEBUG else 'An error occurred while processing your message'
        
        return JsonResponse({
            'success': False,
            'error': error_message,
            'details': error_details if settings.DEBUG else None
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_history_view(request, conversation_id):
    """
    Get conversation history.
    
    Args:
        conversation_id: ID of the conversation
    """
    try:
        chatbot = get_chatbot()
        result = chatbot.get_conversation_history(conversation_id)
        
        # Verify user owns this conversation
        if result.get('success'):
            conversation = ChatConversation.objects.get(id=conversation_id)
            if conversation.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Unauthorized'
                }, status=403)
        
        return JsonResponse(result)
        
    except ChatConversation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Conversation not found'
        }, status=404)
    except Exception as e:
        print(f"Error in get_history_view: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def new_conversation_view(request):
    """
    Start a new conversation.
    Always creates a new conversation, even if one exists with the same context.
    
    POST data:
        - context_type: optional (general/lesson/exercise)
        - context_id: optional (ID of lesson or exercise)
    """
    try:
        data = json.loads(request.body)
        context_type = data.get('context_type', 'general')
        context_id = data.get('context_id')
        
        chatbot = get_chatbot()
        # Force new conversation - don't reuse existing one
        conversation = chatbot.get_or_create_conversation(
            user=request.user,
            context_type=context_type,
            context_id=context_id,
            force_new=True
        )
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'context_type': conversation.context_type,
            'context_id': conversation.context_id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        print(f"Error in new_conversation_view: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def context_conversation_view(request, context_type, context_id):
    """
    Get or create a context-aware conversation.
    
    Args:
        context_type: Type of context (lesson/exercise)
        context_id: ID of the lesson or exercise
    """
    try:
        if context_type not in ['lesson', 'exercise']:
            return JsonResponse({
                'success': False,
                'error': 'Invalid context type'
            }, status=400)
        
        chatbot = get_chatbot()
        conversation = chatbot.get_or_create_conversation(
            user=request.user,
            context_type=context_type,
            context_id=context_id
        )
        
        # Get recent messages
        result = chatbot.get_conversation_history(conversation.id, limit=20)
        
        return JsonResponse(result)
        
    except Exception as e:
        print(f"Error in context_conversation_view: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def list_conversations_view(request):
    """
    List all conversations for the current user.
    """
    try:
        from .models import ChatMessage
        
        conversations = ChatConversation.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-updated_at')[:20]
        
        conversations_data = []
        for conv in conversations:
            # Get last message (any role - user or assistant)
            last_msg = ChatMessage.objects.filter(
                conversation=conv
            ).order_by('-timestamp').first()
            
            # Only include conversations that have at least one message
            if last_msg:
                conversations_data.append({
                    'id': conv.id,
                    'context_type': conv.context_type,
                    'context_id': conv.context_id,
                    'updated_at': conv.updated_at.isoformat(),
                    'last_message': last_msg.content[:50] if last_msg else None
                })
        
        return JsonResponse({
            'success': True,
            'conversations': conversations_data
        })
        
    except Exception as e:
        print(f"Error in list_conversations_view: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def delete_conversation_view(request, conversation_id):
    """
    Delete a conversation (soft delete by setting is_active=False).
    """
    try:
        conversation = ChatConversation.objects.get(
            id=conversation_id,
            user=request.user
        )
        
        # Soft delete
        conversation.is_active = False
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Conversation deleted successfully'
        })
        
    except ChatConversation.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Conversation not found'
        }, status=404)
    except Exception as e:
        print(f"Error in delete_conversation_view: {e}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred'
        }, status=500)


@require_http_methods(["GET"])
def check_api_key_view(request):
    """
    Debug endpoint to check if API key is configured.
    """
    api_key = settings.GEMINI_API_KEY
    return JsonResponse({
        'api_key_configured': bool(api_key),
        'api_key_length': len(api_key) if api_key else 0,
        'api_key_preview': api_key[:10] + '...' if api_key else None,
        'debug_mode': settings.DEBUG
    })
