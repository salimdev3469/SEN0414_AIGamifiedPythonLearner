"""
Tests for AI Tutor views
"""
import pytest
import json
from unittest.mock import patch
from django.urls import reverse
from apps.ai_tutor.models import ChatConversation, ChatMessage
from tests.fixtures.base_fixtures import test_user, authenticated_client, test_lesson, test_exercise


@pytest.mark.unit
@pytest.mark.django_db
class TestSendMessageView:
    """Test send_message_view"""
    
    def test_send_message_requires_login(self, client):
        """Test that send message requires authentication"""
        url = reverse('ai_tutor:send_message')
        response = client.post(url, json.dumps({'message': 'test'}), content_type='application/json')
        
        assert response.status_code == 302  # Redirect to login
    
    def test_send_message_empty_message(self, authenticated_client):
        """Test sending empty message returns error"""
        url = reverse('ai_tutor:send_message')
        response = authenticated_client.post(
            url,
            json.dumps({'message': ''}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'empty' in data['error'].lower()
    
    @patch('apps.ai_tutor.views.get_chatbot')
    def test_send_message_success(self, mock_get_chatbot, authenticated_client):
        """Test successful message sending"""
        from unittest.mock import MagicMock
        
        # Mock chatbot
        mock_chatbot = MagicMock()
        mock_chatbot.send_message.return_value = {
            'success': True,
            'message': 'Test response',
            'conversation_id': 1,
            'message_id': 1,
            'tokens_used': 10
        }
        mock_get_chatbot.return_value = mock_chatbot
        
        url = reverse('ai_tutor:send_message')
        response = authenticated_client.post(
            url,
            json.dumps({'message': 'Hello'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['message'] == 'Test response'
    
    def test_send_message_invalid_json(self, authenticated_client):
        """Test sending invalid JSON"""
        url = reverse('ai_tutor:send_message')
        response = authenticated_client.post(
            url,
            'invalid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False


@pytest.mark.unit
@pytest.mark.django_db
class TestGetHistoryView:
    """Test get_history_view"""
    
    def test_get_history_requires_login(self, client):
        """Test that get history requires authentication"""
        url = reverse('ai_tutor:get_history', args=[1])
        response = client.get(url)
        
        assert response.status_code == 302
    
    @patch('apps.ai_tutor.views.get_chatbot')
    def test_get_history_not_found(self, mock_get_chatbot, authenticated_client):
        """Test getting history for non-existent conversation"""
        from unittest.mock import MagicMock
        
        mock_chatbot = MagicMock()
        mock_chatbot.get_conversation_history.return_value = {
            'success': False,
            'error': 'Conversation not found'
        }
        mock_get_chatbot.return_value = mock_chatbot
        
        url = reverse('ai_tutor:get_history', args=[99999])
        response = authenticated_client.get(url)
        
        assert response.status_code == 200  # View returns 200 with error in JSON
        data = json.loads(response.content)
        assert data['success'] is False
    
    def test_get_history_unauthorized(self, authenticated_client, test_user):
        """Test getting history for another user's conversation"""
        from apps.authentication.models import User
        
        # Create another user and conversation
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        conversation = ChatConversation.objects.create(
            user=other_user,
            context_type='general'
        )
        
        url = reverse('ai_tutor:get_history', args=[conversation.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == 403
        data = json.loads(response.content)
        assert data['success'] is False
    
    @patch('apps.ai_tutor.views.get_chatbot')
    def test_get_history_success(self, mock_get_chatbot, authenticated_client, test_user):
        """Test successful history retrieval"""
        from unittest.mock import MagicMock
        
        conversation = ChatConversation.objects.create(
            user=test_user,
            context_type='general'
        )
        
        mock_chatbot = MagicMock()
        mock_chatbot.get_conversation_history.return_value = {
            'success': True,
            'messages': [],
            'conversation': {
                'id': conversation.id,
                'context_type': 'general',
                'context_id': None
            }
        }
        mock_get_chatbot.return_value = mock_chatbot
        
        url = reverse('ai_tutor:get_history', args=[conversation.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True


@pytest.mark.unit
@pytest.mark.django_db
class TestNewConversationView:
    """Test new_conversation_view"""
    
    def test_new_conversation_requires_login(self, client):
        """Test that new conversation requires authentication"""
        url = reverse('ai_tutor:new_conversation')
        response = client.post(url, json.dumps({}), content_type='application/json')
        
        assert response.status_code == 302
    
    @patch('apps.ai_tutor.views.get_chatbot')
    def test_new_conversation_success(self, mock_get_chatbot, authenticated_client, test_user):
        """Test creating new conversation"""
        from unittest.mock import MagicMock
        
        conversation = ChatConversation.objects.create(
            user=test_user,
            context_type='general'
        )
        
        mock_chatbot = MagicMock()
        mock_chatbot.get_or_create_conversation.return_value = conversation
        mock_get_chatbot.return_value = mock_chatbot
        
        url = reverse('ai_tutor:new_conversation')
        response = authenticated_client.post(
            url,
            json.dumps({'context_type': 'general'}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert data['conversation_id'] == conversation.id
        # Verify force_new=True was called
        mock_chatbot.get_or_create_conversation.assert_called_once_with(
            user=test_user,
            context_type='general',
            context_id=None,
            force_new=True
        )


@pytest.mark.unit
@pytest.mark.django_db
class TestContextConversationView:
    """Test context_conversation_view"""
    
    def test_context_conversation_invalid_type(self, authenticated_client):
        """Test invalid context type"""
        url = reverse('ai_tutor:context_conversation', args=['invalid', 1])
        response = authenticated_client.get(url)
        
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'invalid' in data['error'].lower()
    
    @patch('apps.ai_tutor.views.get_chatbot')
    def test_context_conversation_lesson(self, mock_get_chatbot, authenticated_client, test_user, test_lesson):
        """Test context conversation with lesson"""
        from unittest.mock import MagicMock
        
        conversation = ChatConversation.objects.create(
            user=test_user,
            context_type='lesson',
            context_id=str(test_lesson.id)
        )
        
        mock_chatbot = MagicMock()
        mock_chatbot.get_or_create_conversation.return_value = conversation
        mock_chatbot.get_conversation_history.return_value = {
            'success': True,
            'messages': []
        }
        mock_get_chatbot.return_value = mock_chatbot
        
        url = reverse('ai_tutor:context_conversation', args=['lesson', test_lesson.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True


@pytest.mark.unit
@pytest.mark.django_db
class TestListConversationsView:
    """Test list_conversations_view"""
    
    def test_list_conversations_requires_login(self, client):
        """Test that list conversations requires authentication"""
        url = reverse('ai_tutor:list_conversations')
        response = client.get(url)
        
        assert response.status_code == 302
    
    def test_list_conversations_success(self, authenticated_client, test_user):
        """Test listing conversations"""
        # Create conversations with messages
        conv1 = ChatConversation.objects.create(
            user=test_user,
            context_type='general'
        )
        ChatMessage.objects.create(
            conversation=conv1,
            role='user',
            content='Hello'
        )
        
        conv2 = ChatConversation.objects.create(
            user=test_user,
            context_type='lesson',
            context_id='1'
        )
        ChatMessage.objects.create(
            conversation=conv2,
            role='user',
            content='Question'
        )
        
        url = reverse('ai_tutor:list_conversations')
        response = authenticated_client.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert len(data['conversations']) == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestDeleteConversationView:
    """Test delete_conversation_view"""
    
    def test_delete_conversation_requires_login(self, client):
        """Test that delete conversation requires authentication"""
        url = reverse('ai_tutor:delete_conversation', args=[1])
        response = client.post(url)
        
        assert response.status_code == 302
    
    def test_delete_conversation_not_found(self, authenticated_client):
        """Test deleting non-existent conversation"""
        url = reverse('ai_tutor:delete_conversation', args=[99999])
        response = authenticated_client.post(url)
        
        assert response.status_code == 404
        data = json.loads(response.content)
        assert data['success'] is False
    
    def test_delete_conversation_success(self, authenticated_client, test_user):
        """Test successful conversation deletion"""
        conversation = ChatConversation.objects.create(
            user=test_user,
            context_type='general',
            is_active=True
        )
        
        url = reverse('ai_tutor:delete_conversation', args=[conversation.id])
        response = authenticated_client.post(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        
        # Verify soft delete
        conversation.refresh_from_db()
        assert conversation.is_active is False
    
    def test_delete_conversation_unauthorized(self, authenticated_client):
        """Test deleting another user's conversation"""
        from apps.authentication.models import User
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        conversation = ChatConversation.objects.create(
            user=other_user,
            context_type='general'
        )
        
        url = reverse('ai_tutor:delete_conversation', args=[conversation.id])
        response = authenticated_client.post(url)
        
        assert response.status_code == 404  # Not found for unauthorized user


@pytest.mark.unit
class TestCheckApiKeyView:
    """Test check_api_key_view"""
    
    def test_check_api_key_view(self, client):
        """Test API key check endpoint"""
        url = reverse('ai_tutor:check_api_key')
        response = client.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'api_key_configured' in data
        assert 'debug_mode' in data

