"""
Utility functions for the AI Tutor app.
"""

import google.generativeai as genai
from django.conf import settings
from django.core.cache import cache
import json
import hashlib
from .models import ChatConversation, ChatMessage
from .rate_limiter import check_gemini_rate_limit


class GeminiChatbot:
    """
    AI Chatbot using Google Gemini API.
    Provides context-aware Python tutoring with conversation history.
    """
    
    def __init__(self):
        """Initialize Gemini API with API key from settings."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
        self.max_history_messages = 10  # Limit conversation history for API efficiency
    
    def get_or_create_conversation(self, user, context_type='general', context_id=None, force_new=False):
        """
        Get or create a conversation for the user.
        
        Args:
            user: User object
            context_type: Type of context (general/lesson/exercise)
            context_id: ID of the lesson or exercise (if context-aware)
            force_new: If True, always create a new conversation (don't reuse existing)
        
        Returns:
            ChatConversation object
        """
        if not force_new:
            # Try to get active conversation with same context
            conversation = ChatConversation.objects.filter(
                user=user,
                context_type=context_type,
                context_id=context_id,
                is_active=True
            ).first()
            
            if conversation:
                return conversation
        
        # Create new conversation
        conversation = ChatConversation.objects.create(
            user=user,
            context_type=context_type,
            context_id=context_id,
            is_active=True
        )
        
        return conversation
    
    def send_message(self, user, message_content, context_type='general', context_id=None, code_snippet=None):
        """
        Send a message and get AI response.
        
        Args:
            user: User object
            message_content: User's message
            context_type: Type of context (general/lesson/exercise)
            context_id: ID of the lesson or exercise
            code_snippet: Optional code snippet for debugging
        
        Returns:
            dict: Response with assistant message and metadata
        """
        # Get or create conversation
        conversation = self.get_or_create_conversation(user, context_type, context_id)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=message_content
        )
        
        try:
            # Debug: Print context info
            print(f"[DEBUG] Sending message with context_type={context_type}, context_id={context_id}")
            
            # Build prompt with context and history
            prompt = self._build_prompt(
                conversation=conversation,
                user_message=message_content,
                context_type=context_type,
                context_id=context_id,
                code_snippet=code_snippet
            )
            
            # Debug: Print first 500 chars of prompt to verify context is included
            print(f"[DEBUG] Prompt preview (first 500 chars): {prompt[:500]}")
            
            # Check cache for similar questions
            cache_key = self._get_cache_key(message_content, context_type, context_id)
            cached_response = cache.get(cache_key)
            
            if cached_response:
                assistant_content = cached_response
                tokens_used = 0  # Cached response
            else:
                # Check rate limit before making API call
                allowed, remaining, reset_time = check_gemini_rate_limit()
                if not allowed:
                    assistant_content = (
                        f"⚠️ Günlük API limitine ulaşıldı. "
                        f"Lütfen {reset_time.strftime('%H:%M')} saatinden sonra tekrar deneyin. "
                        f"Günlük limit: 100 istek."
                    )
                    tokens_used = 0
                else:
                    # Generate response from Gemini
                    response = self.model.generate_content(
                        prompt,
                        generation_config={
                            'temperature': 0.7,
                            'top_p': 0.9,
                            'top_k': 40,
                            'max_output_tokens': 2048,
                        }
                    )
                
                if response and response.text:
                    assistant_content = response.text.strip()
                    # Estimate tokens (rough approximation)
                    tokens_used = len(prompt.split()) + len(assistant_content.split())
                    
                    # Cache the response for 1 hour
                    cache.set(cache_key, assistant_content, 3600)
                else:
                    assistant_content = "I apologize, but I'm having trouble generating a response right now. Please try again."
                    tokens_used = 0
            
            # Save assistant message
            assistant_message = ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=assistant_content,
                tokens_used=tokens_used
            )
            
            return {
                'success': True,
                'message': assistant_content,
                'conversation_id': conversation.id,
                'message_id': assistant_message.id,
                'tokens_used': tokens_used
            }
            
        except Exception as e:
            error_str = str(e)
            print(f"Error in chatbot: {e}")
            
            # Check for quota errors
            if '429' in error_str or 'quota' in error_str.lower():
                error_message = "⚠️ I'm currently experiencing high demand. Please try again in a few moments."
            else:
                error_message = "I apologize, but I encountered an error. Please try rephrasing your question."
            
            # Save error as assistant message
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=error_message,
                tokens_used=0
            )
            
            return {
                'success': False,
                'error': error_message,
                'conversation_id': conversation.id
            }
    
    def get_conversation_history(self, conversation_id, limit=50):
        """
        Get conversation history.
        
        Args:
            conversation_id: ID of the conversation
            limit: Maximum number of messages to retrieve
        
        Returns:
            list: List of message dictionaries
        """
        try:
            conversation = ChatConversation.objects.get(id=conversation_id)
            messages = conversation.messages.order_by('timestamp')[:limit]
            
            return {
                'success': True,
                'messages': [
                    {
                        'id': msg.id,
                        'role': msg.role,
                        'content': msg.content,
                        'timestamp': msg.timestamp.isoformat(),
                    }
                    for msg in messages
                ],
                'conversation': {
                    'id': conversation.id,
                    'context_type': conversation.context_type,
                    'context_id': conversation.context_id,
                    'created_at': conversation.created_at.isoformat(),
                }
            }
        except ChatConversation.DoesNotExist:
            return {
                'success': False,
                'error': 'Conversation not found'
            }
    
    def _detect_language(self, text):
        """
        Detect if the text is in Turkish or English.
        
        Args:
            text: User message text
        
        Returns:
            str: 'turkish' or 'english'
        """
        if not text:
            return 'english'
        
        text_lower = text.lower()
        
        # Turkish-specific characters and common words
        turkish_chars = ['ç', 'ğ', 'ı', 'ö', 'ş', 'ü']
        turkish_words = ['nasıl', 'neden', 'ne', 'bu', 'şu', 'o', 'var', 'yok', 
                         've', 'ile', 'için', 'gibi', 'kadar', 'daha', 'en', 
                         'çok', 'az', 'bir', 'iki', 'üç', 'hata', 'kod', 'çalışmıyor',
                         'anlamadım', 'açıklayabilir', 'misin', 'mısın', 'mı', 'mi',
                         'yapmak', 'etmek', 'olmak', 'gelmek', 'gitmek']
        
        # Check for Turkish characters
        has_turkish_chars = any(char in text_lower for char in turkish_chars)
        
        # Check for Turkish words
        turkish_word_count = sum(1 for word in turkish_words if word in text_lower)
        
        # If has Turkish chars or 2+ Turkish words, likely Turkish
        if has_turkish_chars or turkish_word_count >= 2:
            return 'turkish'
        
        return 'english'
    
    def _build_prompt(self, conversation, user_message, context_type, context_id, code_snippet=None):
        """
        Build the prompt with context and conversation history.
        
        Args:
            conversation: ChatConversation object
            user_message: Current user message
            context_type: Type of context
            context_id: Context ID
            code_snippet: Optional code snippet
        
        Returns:
            str: Complete prompt for Gemini
        """
        # Detect user's language
        detected_language = self._detect_language(user_message)
        
        # Check conversation history for language consistency
        recent_messages = conversation.messages.order_by('-timestamp')[:3]
        if recent_messages:
            # Check last few messages to determine language
            for msg in recent_messages:
                if msg.role == 'user':
                    lang = self._detect_language(msg.content)
                    if lang == 'turkish':
                        detected_language = 'turkish'
                        break
        
        # Language-specific system prompt
        if detected_language == 'turkish':
            system_prompt = """Sen uzman bir Python programlama öğretmeni ve mentorusun. Görevin:

1. **Python sorularını açık ve doğru bir şekilde cevaplamak**
2. **Yardımcı kod örnekleri ve açıklamalar sağlamak**
3. **Kod hatalarını düzeltmek ve hataları dostane bir şekilde açıklamak**
4. **Öğrenmeyi ve en iyi uygulamaları teşvik etmek**
5. **Sabırlı ve destekleyici olmak**

Kurallar:
- Kod blokları için markdown formatı kullan (```python)
- Açıklamaları kısa ama kapsamlı tut
- İlgili olduğunda çalıştırılabilir kod örnekleri ver
- Sadece NASIL değil, NEDEN'i açıkla
- İyi kodlama uygulamalarını teşvik et (PEP 8, okunabilirlik, vb.)
- Kullanıcının kodunda hatalar varsa, bunları açıkça açıkla ve düzeltmeler öner
- Cesaret verici ve pozitif ol

**ÇOK ÖNEMLİ DİL TALİMATI:**
Kullanıcı Türkçe yazıyorsa, SEN DE TÜRKÇE CEVAP VER. Kullanıcı İngilizce yazıyorsa, İngilizce cevap ver. Kullanıcının dilini otomatik olarak algıla ve aynı dilde cevap ver. Sadece kod örnekleri ve teknik terimler gerekirse İngilizce kalabilir, ama tüm açıklamalar kullanıcının dilinde olmalı.

"""
        else:
            system_prompt = """You are an expert Python programming tutor and mentor. Your role is to:

1. **Answer Python questions clearly and accurately**
2. **Provide helpful code examples with explanations**
3. **Debug code and explain errors in a friendly way**
4. **Encourage learning and best practices**
5. **Be patient and supportive**

Guidelines:
- Use markdown formatting for code blocks (```python)
- Keep explanations concise but thorough
- Provide runnable code examples when relevant
- Explain WHY, not just HOW
- Encourage good coding practices (PEP 8, readability, etc.)
- If the user's code has errors, explain them clearly and suggest fixes
- Be encouraging and positive

**CRITICAL LANGUAGE INSTRUCTION:**
Detect the language the user is writing in and respond in the SAME language. If the user writes in Turkish, respond in Turkish. If the user writes in English, respond in English. Match the user's language automatically. Only code examples and technical terms can remain in English if necessary, but all explanations must match the user's language.

"""
        
        # Add context-specific information
        context_prompt = self._get_context_prompt(context_type, context_id)
        
        # Build conversation history
        history_prompt = self._build_conversation_history(conversation)
        
        # Add code snippet if provided
        code_prompt = ""
        if code_snippet:
            code_prompt = f"\n\n**User's Code:**\n```python\n{code_snippet}\n```\n"
        
        # Add explicit language instruction based on detection
        language_instruction = ""
        if detected_language == 'turkish':
            language_instruction = "\n**DİL TALİMATI:** Kullanıcı Türkçe yazıyor. LÜTFEN TÜRKÇE CEVAP VER. Tüm açıklamaları Türkçe yap, sadece kod örnekleri İngilizce kalabilir.\n"
        else:
            language_instruction = "\n**LANGUAGE INSTRUCTION:** The user is writing in English. Please respond in ENGLISH. All explanations should be in English.\n"
        
        # Combine all parts
        full_prompt = f"""{system_prompt}

{context_prompt}

{history_prompt}
{language_instruction}
**Current User Question:**
{user_message}
{code_prompt}

**Your Response:**
"""
        
        return full_prompt
    
    def _get_context_prompt(self, context_type, context_id):
        """
        Get context-specific prompt information.
        
        Args:
            context_type: Type of context
            context_id: Context ID
        
        Returns:
            str: Context prompt
        """
        if context_type == 'lesson' and context_id:
            try:
                from apps.learning.models import Lesson
                lesson = Lesson.objects.get(id=context_id)
                # Get lesson content (first 500 chars for context)
                lesson_content_preview = lesson.content[:500] if lesson.content else "No content available"
                return f"""**Current Context: Lesson**
- **Topic:** {lesson.title}
- **Module:** {lesson.module.title if lesson.module else 'N/A'}
- **Lesson Content Preview:** {lesson_content_preview}...

**IMPORTANT:** The user is currently studying this specific lesson. Your responses should be directly related to this lesson's content and topic. Reference specific concepts, examples, or code from this lesson when answering questions. If the user asks about something not covered in this lesson, gently guide them back to the current lesson material or suggest they complete this lesson first.

When the user says they don't understand something, explain it in the context of this lesson's content.
"""
            except Exception as e:
                print(f"Error getting lesson context: {e}")
                import traceback
                traceback.print_exc()
                pass
        
        elif context_type == 'exercise' and context_id:
            try:
                from apps.coding.models import Exercise
                exercise = Exercise.objects.get(id=context_id)
                # Get exercise description and problem statement
                problem_statement = exercise.description[:500] if exercise.description else "No description available"
                return f"""**Current Context: Coding Exercise**
- **Exercise:** {exercise.title}
- **Difficulty:** {exercise.get_difficulty_display()}
- **Problem Statement:** {problem_statement}...

**IMPORTANT:** The user is currently working on this specific coding exercise. Your responses should be directly related to this exercise. Help them understand the problem requirements and guide them toward a solution WITHOUT giving away the complete answer. Provide hints, explain concepts, and help debug their code, but let them write the solution themselves.

When the user says they don't understand, explain the exercise requirements and guide them step by step.
"""
            except Exception as e:
                print(f"Error getting exercise context: {e}")
                import traceback
                traceback.print_exc()
                pass
        
        return "**Context:** General Python tutoring"
    
    def _build_conversation_history(self, conversation):
        """
        Build conversation history for context.
        
        Args:
            conversation: ChatConversation object
        
        Returns:
            str: Formatted conversation history
        """
        # Get recent messages
        messages = conversation.messages.order_by('-timestamp')[:self.max_history_messages]
        messages = list(reversed(messages))  # Chronological order
        
        if not messages:
            return "**Conversation History:** (New conversation)"
        
        history_lines = ["**Recent Conversation:**"]
        for msg in messages[:-1]:  # Exclude the current message
            role_label = "User" if msg.role == 'user' else "Assistant"
            content_preview = msg.content[:150] + "..." if len(msg.content) > 150 else msg.content
            history_lines.append(f"- **{role_label}:** {content_preview}")
        
        return "\n".join(history_lines)
    
    def _get_cache_key(self, message, context_type, context_id):
        """
        Generate cache key for a message.
        
        Args:
            message: User message
            context_type: Context type
            context_id: Context ID
        
        Returns:
            str: Cache key
        """
        # Create a hash of the message and context
        content = f"{message}:{context_type}:{context_id}"
        hash_object = hashlib.md5(content.encode())
        return f"chatbot_response_{hash_object.hexdigest()}"


# Global instance
_chatbot_instance = None


def get_chatbot():
    """Get or create chatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = GeminiChatbot()
    return _chatbot_instance

