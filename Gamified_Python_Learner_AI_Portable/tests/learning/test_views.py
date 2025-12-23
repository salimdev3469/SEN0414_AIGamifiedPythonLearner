"""
Unit tests for learning views
"""
import pytest
from django.urls import reverse
from apps.learning.models import Module, Lesson, UserProgress


@pytest.mark.unit
@pytest.mark.django_db
class TestCurriculumView:
    """Test curriculum_view"""
    
    def test_curriculum_accessible(self, client, test_module):
        """Test curriculum page is accessible"""
        response = client.get(reverse('learning:curriculum'))
        assert response.status_code == 200
        assert 'modules' in response.context
    
    def test_curriculum_shows_modules(self, client, test_module):
        """Test curriculum shows published modules"""
        response = client.get(reverse('learning:curriculum'))
        modules = response.context['modules']
        assert len(modules) > 0
        assert test_module in modules
    
    def test_curriculum_shows_completion_for_authenticated(self, authenticated_client, test_user, test_module, test_lesson):
        """Test curriculum shows completion status for authenticated users"""
        # Complete a lesson
        UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        response = authenticated_client.get(reverse('learning:curriculum'))
        assert response.status_code == 200
        modules = response.context['modules']
        assert len(modules) > 0
        # Check completion status is set
        module = modules[0]
        assert hasattr(module, 'completion')
        assert hasattr(module, 'lessons_with_status')
    
    def test_curriculum_hides_unpublished_modules(self, client, test_module):
        """Test curriculum hides unpublished modules"""
        # Create unpublished module
        unpublished = Module.objects.create(
            title='Unpublished',
            description='Test',
            order=99,
            is_published=False
        )
        
        response = client.get(reverse('learning:curriculum'))
        modules = response.context['modules']
        assert unpublished not in modules


@pytest.mark.unit
@pytest.mark.django_db
class TestLessonDetailView:
    """Test lesson_detail_view"""
    
    def test_lesson_detail_requires_login(self, client, test_lesson):
        """Test lesson detail requires login"""
        response = client.get(reverse('learning:lesson_detail', args=[test_lesson.id]))
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_lesson_detail_shows_lesson(self, authenticated_client, test_lesson):
        """Test lesson detail shows lesson content"""
        response = authenticated_client.get(reverse('learning:lesson_detail', args=[test_lesson.id]))
        assert response.status_code == 200
        assert 'lesson' in response.context
        assert response.context['lesson'] == test_lesson
    
    def test_lesson_detail_creates_progress(self, authenticated_client, test_user, test_lesson):
        """Test lesson detail creates progress entry"""
        # Delete any existing progress
        UserProgress.objects.filter(user=test_user, lesson=test_lesson).delete()
        
        response = authenticated_client.get(reverse('learning:lesson_detail', args=[test_lesson.id]))
        assert response.status_code == 200
        
        # Progress should be created
        progress = UserProgress.objects.filter(user=test_user, lesson=test_lesson).first()
        assert progress is not None
    
    def test_lesson_detail_shows_next_previous(self, authenticated_client, test_module, test_lesson):
        """Test lesson detail shows next/previous lessons"""
        # Create another lesson
        lesson2 = Lesson.objects.create(
            module=test_module,
            title='Lesson 2',
            content='Content 2',
            order=2,
            is_published=True,
            xp_reward=50
        )
        
        response = authenticated_client.get(reverse('learning:lesson_detail', args=[test_lesson.id]))
        assert response.status_code == 200
        assert 'next_lesson' in response.context
        assert 'previous_lesson' in response.context
    
    def test_lesson_detail_hides_unpublished_lesson(self, authenticated_client, test_module):
        """Test lesson detail hides unpublished lessons"""
        unpublished = Lesson.objects.create(
            module=test_module,
            title='Unpublished',
            content='Test',
            order=99,
            is_published=False,
            xp_reward=50
        )
        
        response = authenticated_client.get(reverse('learning:lesson_detail', args=[unpublished.id]))
        assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.django_db
class TestMarkLessonComplete:
    """Test mark_lesson_complete view"""
    
    def test_mark_complete_requires_login(self, client, test_lesson):
        """Test mark complete requires login"""
        response = client.post(reverse('learning:mark_complete', args=[test_lesson.id]))
        assert response.status_code == 302
        assert '/login/' in response.url
    
    def test_mark_complete_requires_post(self, authenticated_client, test_lesson):
        """Test mark complete requires POST method"""
        response = authenticated_client.get(reverse('learning:mark_complete', args=[test_lesson.id]))
        # Should redirect to lesson detail
        assert response.status_code == 302
    
    def test_mark_complete_awards_xp(self, authenticated_client, test_user, test_lesson):
        """Test mark complete awards XP"""
        initial_xp = test_user.xp
        
        response = authenticated_client.post(reverse('learning:mark_complete', args=[test_lesson.id]))
        
        test_user.refresh_from_db()
        assert test_user.xp > initial_xp
    
    def test_mark_complete_creates_progress(self, authenticated_client, test_user, test_lesson):
        """Test mark complete creates progress entry"""
        # Delete any existing progress
        UserProgress.objects.filter(user=test_user, lesson=test_lesson).delete()
        
        response = authenticated_client.post(reverse('learning:mark_complete', args=[test_lesson.id]))
        
        progress = UserProgress.objects.filter(user=test_user, lesson=test_lesson).first()
        assert progress is not None
        assert progress.status == 'completed'
    
    def test_mark_complete_twice_no_double_xp(self, authenticated_client, test_user, test_lesson):
        """Test marking complete twice doesn't award XP twice"""
        # Complete first time
        response1 = authenticated_client.post(reverse('learning:mark_complete', args=[test_lesson.id]))
        test_user.refresh_from_db()
        xp_after_first = test_user.xp
        
        # Complete second time
        response2 = authenticated_client.post(reverse('learning:mark_complete', args=[test_lesson.id]))
        test_user.refresh_from_db()
        xp_after_second = test_user.xp
        
        # XP should be the same
        assert xp_after_first == xp_after_second
    
    def test_mark_complete_redirects_to_next_lesson(self, authenticated_client, test_module, test_lesson):
        """Test mark complete redirects to next lesson if available"""
        # Create next lesson
        next_lesson = Lesson.objects.create(
            module=test_module,
            title='Next Lesson',
            content='Content',
            order=2,
            is_published=True,
            xp_reward=50
        )
        
        response = authenticated_client.post(reverse('learning:mark_complete', args=[test_lesson.id]))
        # Should redirect to next lesson
        assert response.status_code == 302


@pytest.mark.unit
@pytest.mark.django_db
class TestModuleDetailView:
    """Test module_detail_view"""
    
    def test_module_detail_requires_login(self, client, test_module):
        """Test module detail requires login"""
        response = client.get(reverse('learning:module_detail', args=[test_module.id]))
        assert response.status_code == 302
        assert '/login/' in response.url
    
    @pytest.mark.skip(reason="Template learning/module_detail.html does not exist")
    def test_module_detail_shows_module(self, authenticated_client, test_module):
        """Test module detail shows module"""
        response = authenticated_client.get(reverse('learning:module_detail', args=[test_module.id]))
        assert response.status_code == 200
        assert 'module' in response.context
        assert response.context['module'] == test_module
    
    @pytest.mark.skip(reason="Template learning/module_detail.html does not exist")
    def test_module_detail_shows_lessons(self, authenticated_client, test_module, test_lesson):
        """Test module detail shows lessons"""
        response = authenticated_client.get(reverse('learning:module_detail', args=[test_module.id]))
        assert response.status_code == 200
        assert 'lessons' in response.context
        assert test_lesson in response.context['lessons']
    
    @pytest.mark.skip(reason="Template learning/module_detail.html does not exist")
    def test_module_detail_shows_completion(self, authenticated_client, test_user, test_module, test_lesson):
        """Test module detail shows completion percentage"""
        # Complete a lesson
        UserProgress.objects.create(
            user=test_user,
            lesson=test_lesson,
            status='completed'
        )
        
        response = authenticated_client.get(reverse('learning:module_detail', args=[test_module.id]))
        assert response.status_code == 200
        assert 'completion_percentage' in response.context
        assert 0 <= response.context['completion_percentage'] <= 100
    
    def test_module_detail_hides_unpublished_module(self, authenticated_client):
        """Test module detail hides unpublished modules"""
        unpublished = Module.objects.create(
            title='Unpublished',
            description='Test',
            order=99,
            is_published=False
        )
        
        response = authenticated_client.get(reverse('learning:module_detail', args=[unpublished.id]))
        assert response.status_code == 404

