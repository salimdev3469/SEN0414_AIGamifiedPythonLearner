"""
Tests for AI Tutor utils
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.core.cache import cache
from django.utils import timezone
from apps.ai_tutor.utils import GeminiChatbot, get_chatbot
from apps.ai_tutor.models import ChatConversation, ChatMessage
from tests.fixtures.base_fixtures import test_user, test_lesson, test_exercise


@pytest.mark.unit
@pytest.mark.django_db
class TestGeminiChatbot:
    """Test GeminiChatbot class"""
    
    def test_chatbot_initialization(self):
        """Test chatbot can be initialized"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot = GeminiChatbot()
            assert chatbot.max_history_messages == 10
    
    def test_get_or_create_conversation_creates_new(self, test_user):
        """Test creating a new conversation"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot = GeminiChatbot()
            conversation = chatbot.get_or_create_conversation(
                user=test_user,
                context_type='general'
            )
            
            assert conversation is not None
            assert conversation.user == test_user
            assert conversation.context_type == 'general'
            assert conversation.is_active is True
    
    def test_get_or_create_conversation_reuses_existing(self, test_user):
        """Test reusing existing conversation"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot = GeminiChatbot()
            
            # Create first conversation
            conv1 = chatbot.get_or_create_conversation(
                user=test_user,
                context_type='general'
            )
            
            # Get or create should return same conversation
            conv2 = chatbot.get_or_create_conversation(
                user=test_user,
                context_type='general'
            )
            
            assert conv1.id == conv2.id
    
    def test_get_or_create_conversation_force_new(self, test_user):
        """Test force_new creates new conversation"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot = GeminiChatbot()
            
            # Create first conversation
            conv1 = chatbot.get_or_create_conversation(
                user=test_user,
                context_type='general'
            )
            
            # Force new should create different conversation
            conv2 = chatbot.get_or_create_conversation(
                user=test_user,
                context_type='general',
                force_new=True
            )
            
            assert conv1.id != conv2.id
    
    def test_get_or_create_conversation_with_context(self, test_user, test_lesson):
        """Test conversation with lesson context"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot = GeminiChatbot()
            conversation = chatbot.get_or_create_conversation(
                user=test_user,
                context_type='lesson',
                context_id=test_lesson.id
            )
            
            assert conversation.context_type == 'lesson'
            assert str(conversation.context_id) == str(test_lesson.id)
    
    @patch('apps.ai_tutor.utils.check_gemini_rate_limit')
    @patch('apps.ai_tutor.utils.genai.configure')
    @patch('apps.ai_tutor.utils.genai.GenerativeModel')
    def test_send_message_rate_limit_exceeded(self, mock_model, mock_configure, mock_rate_limit, test_user):
        """Test send_message when rate limit is exceeded"""
        # Setup mocks
        mock_rate_limit.return_value = (False, 0, timezone.now())
        mock_model_instance = MagicMock()
        mock_model.return_value = mock_model_instance
        
        chatbot = GeminiChatbot()
        chatbot.model = mock_model_instance
        
        result = chatbot.send_message(
            user=test_user,
            message_content="Test message"
        )
        
        assert result['success'] is False
        # Error message should indicate rate limit
        assert 'error' in result
    
    @patch('apps.ai_tutor.utils.check_gemini_rate_limit')
    @patch('apps.ai_tutor.utils.genai.configure')
    @patch('apps.ai_tutor.utils.genai.GenerativeModel')
    def test_send_message_success(self, mock_model, mock_configure, mock_rate_limit, test_user):
        """Test successful message sending"""
        # Setup mocks
        mock_rate_limit.return_value = (True, 99, timezone.now())
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "This is a test response"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        chatbot = GeminiChatbot()
        chatbot.model = mock_model_instance
        
        # Clear cache to avoid cached responses
        cache.clear()
        
        result = chatbot.send_message(
            user=test_user,
            message_content="Test message"
        )
        
        assert result['success'] is True
        assert result['message'] == "This is a test response"
        assert 'conversation_id' in result
        assert 'message_id' in result
    
    @patch('apps.ai_tutor.utils.check_gemini_rate_limit')
    @patch('apps.ai_tutor.utils.genai.configure')
    @patch('apps.ai_tutor.utils.genai.GenerativeModel')
    def test_send_message_with_lesson_context(self, mock_model, mock_configure, mock_rate_limit, test_user, test_lesson):
        """Test sending message with lesson context"""
        mock_rate_limit.return_value = (True, 99, timezone.now())
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Response with lesson context"
        mock_model_instance.generate_content.return_value = mock_response
        mock_model.return_value = mock_model_instance
        
        chatbot = GeminiChatbot()
        chatbot.model = mock_model_instance
        
        cache.clear()
        
        result = chatbot.send_message(
            user=test_user,
            message_content="What is this lesson about?",
            context_type='lesson',
            context_id=test_lesson.id
        )
        
        assert result['success'] is True
        # Verify context was used in prompt
        call_args = mock_model_instance.generate_content.call_args
        assert call_args is not None
        prompt = call_args[0][0]
        assert 'lesson' in prompt.lower() or 'Lesson' in prompt
    
    def test_get_conversation_history_success(self, test_user):
        """Test getting conversation history"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot = GeminiChatbot()
            conversation = chatbot.get_or_create_conversation(test_user)
            
            # Add some messages
            ChatMessage.objects.create(
                conversation=conversation,
                role='user',
                content="Hello"
            )
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content="Hi there!"
            )
            
            result = chatbot.get_conversation_history(conversation.id)
            
            assert result['success'] is True
            assert len(result['messages']) == 2
            assert result['messages'][0]['role'] == 'user'
            assert result['messages'][1]['role'] == 'assistant'
    
    def test_get_conversation_history_not_found(self):
        """Test getting history for non-existent conversation"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot = GeminiChatbot()
            result = chatbot.get_conversation_history(99999)
            
            assert result['success'] is False
            assert 'not found' in result['error'].lower()
    
    def test_get_chatbot_singleton(self):
        """Test that get_chatbot returns singleton"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot1 = get_chatbot()
            chatbot2 = get_chatbot()
            
            assert chatbot1 is chatbot2
    
    def test_cache_key_generation(self, test_user):
        """Test cache key generation"""
        with patch('apps.ai_tutor.utils.genai.configure'), \
             patch('apps.ai_tutor.utils.genai.GenerativeModel'):
            chatbot = GeminiChatbot()
            
            key1 = chatbot._get_cache_key("test message", "general", None)
            key2 = chatbot._get_cache_key("test message", "general", None)
            key3 = chatbot._get_cache_key("different message", "general", None)
            
            assert key1 == key2  # Same message = same key
            assert key1 != key3  # Different message = different key
            assert key1.startswith("chatbot_response_")

