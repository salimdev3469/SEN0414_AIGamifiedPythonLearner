"""
Tests for coding views
"""
import pytest
import json
from django.urls import reverse
from apps.authentication.models import User
from apps.learning.models import Module, Lesson, UserProgress
from apps.coding.models import Exercise, TestCase as ExerciseTestCase, UserSubmission


@pytest.fixture
def user(db):
    """Create a test user"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123!'
    )


@pytest.fixture
def module(db):
    """Create a test module"""
    return Module.objects.create(
        title='Python Basics',
        description='Learn Python',
        order=1,
        is_published=True
    )


@pytest.fixture
def lesson(db, module):
    """Create a test lesson"""
    return Lesson.objects.create(
        module=module,
        title='Variables',
        content='Learn about variables',
        order=1,
        is_published=True
    )


@pytest.fixture
def exercise(db, lesson):
    """Create a test exercise"""
    return Exercise.objects.create(
        lesson=lesson,
        title='Add Two Numbers',
        description='Write a function that adds two numbers',
        difficulty='easy',
        starter_code='def add(a, b):\n    # Your code here\n    pass',
        solution_code='def add(a, b):\n    return a + b',
        hints=['Think about the + operator', 'Use return statement'],
        order=1,
        is_published=True
    )


@pytest.fixture
def test_case(db, exercise):
    """Create a test case for exercise"""
    return ExerciseTestCase.objects.create(
        exercise=exercise,
        input_data='{"a": 2, "b": 3}',
        expected_output='5',
        is_hidden=False,
        order=1
    )


@pytest.fixture
def authenticated_client(client, user):
    """Return a client with authenticated user"""
    client.force_login(user)
    return client


class TestExerciseListView:
    """Tests for exercise_list_view"""
    
    def test_exercise_list_requires_login(self, client, lesson):
        """Test that exercise list requires login"""
        response = client.get(
            reverse('coding:exercise_list', kwargs={'lesson_id': lesson.id})
        )
        assert response.status_code == 302
    
    def test_exercise_list_redirects_if_not_completed(self, authenticated_client, lesson, exercise):
        """Test that exercise list redirects if lesson not completed"""
        response = authenticated_client.get(
            reverse('coding:exercise_list', kwargs={'lesson_id': lesson.id})
        )
        # Should redirect to lesson detail
        assert response.status_code == 302
    
    def test_exercise_list_shows_exercises(self, authenticated_client, user, lesson, exercise):
        """Test that exercise list shows exercises after lesson completed"""
        # Complete the lesson first
        UserProgress.objects.create(
            user=user,
            lesson=lesson,
            status='completed'
        )
        
        response = authenticated_client.get(
            reverse('coding:exercise_list', kwargs={'lesson_id': lesson.id})
        )
        
        assert response.status_code == 200
        assert 'exercises' in response.context
    
    def test_exercise_list_nonexistent_lesson(self, authenticated_client):
        """Test exercise list for nonexistent lesson"""
        response = authenticated_client.get(
            reverse('coding:exercise_list', kwargs={'lesson_id': 99999})
        )
        assert response.status_code == 404


class TestExerciseDetailView:
    """Tests for exercise_detail_view"""
    
    def test_exercise_detail_requires_login(self, client, exercise):
        """Test that exercise detail requires login"""
        response = client.get(
            reverse('coding:exercise_detail', kwargs={'exercise_id': exercise.id})
        )
        assert response.status_code == 302
    
    def test_exercise_detail_redirects_if_not_completed(self, authenticated_client, exercise):
        """Test that exercise detail redirects if lesson not completed"""
        response = authenticated_client.get(
            reverse('coding:exercise_detail', kwargs={'exercise_id': exercise.id})
        )
        # Should redirect to lesson detail
        assert response.status_code == 302
    
    def test_exercise_detail_shows_content(self, authenticated_client, user, exercise, lesson):
        """Test that exercise detail shows content"""
        # Complete the lesson first
        UserProgress.objects.create(
            user=user,
            lesson=lesson,
            status='completed'
        )
        
        response = authenticated_client.get(
            reverse('coding:exercise_detail', kwargs={'exercise_id': exercise.id})
        )
        
        assert response.status_code == 200
        assert 'exercise' in response.context
        assert response.context['exercise'] == exercise
    
    def test_exercise_detail_shows_test_cases(self, authenticated_client, user, exercise, lesson, test_case):
        """Test that exercise detail shows visible test cases"""
        # Complete the lesson first
        UserProgress.objects.create(
            user=user,
            lesson=lesson,
            status='completed'
        )
        
        response = authenticated_client.get(
            reverse('coding:exercise_detail', kwargs={'exercise_id': exercise.id})
        )
        
        assert response.status_code == 200
        assert 'visible_test_cases' in response.context
    
    def test_exercise_detail_nonexistent(self, authenticated_client):
        """Test exercise detail for nonexistent exercise"""
        response = authenticated_client.get(
            reverse('coding:exercise_detail', kwargs={'exercise_id': 99999})
        )
        assert response.status_code == 404


class TestAllExercisesView:
    """Tests for all_exercises_view"""
    
    def test_all_exercises_requires_login(self, client):
        """Test that all exercises view requires login"""
        response = client.get(reverse('coding:all_exercises'))
        assert response.status_code == 302
    
    def test_all_exercises_shows_page(self, authenticated_client):
        """Test that all exercises view shows page"""
        response = authenticated_client.get(reverse('coding:all_exercises'))
        
        assert response.status_code == 200
        assert 'lessons_with_exercises' in response.context
    
    def test_all_exercises_shows_completed_lessons(self, authenticated_client, user, lesson, exercise):
        """Test that all exercises view shows exercises for completed lessons"""
        # Complete the lesson first
        UserProgress.objects.create(
            user=user,
            lesson=lesson,
            status='completed'
        )
        
        response = authenticated_client.get(reverse('coding:all_exercises'))
        
        assert response.status_code == 200
        assert len(response.context['lessons_with_exercises']) == 1


class TestSubmitCodeView:
    """Tests for submit_code view"""
    
    def test_submit_code_requires_login(self, client, exercise):
        """Test that submit code requires login"""
        response = client.post(
            reverse('coding:submit_code', kwargs={'exercise_id': exercise.id}),
            data=json.dumps({'code': 'print("hello")'}),
            content_type='application/json'
        )
        assert response.status_code == 302
    
    def test_submit_code_requires_lesson_completion(self, authenticated_client, exercise):
        """Test that lesson must be completed first"""
        code = 'def add(a, b):\n    return a + b'
        
        response = authenticated_client.post(
            reverse('coding:submit_code', kwargs={'exercise_id': exercise.id}),
            data=json.dumps({'code': code}),
            content_type='application/json'
        )
        
        assert response.status_code == 403
    
    def test_submit_code_empty(self, authenticated_client, user, exercise, lesson):
        """Test submitting empty code"""
        # Complete the lesson first
        UserProgress.objects.create(
            user=user,
            lesson=lesson,
            status='completed'
        )
        
        response = authenticated_client.post(
            reverse('coding:submit_code', kwargs={'exercise_id': exercise.id}),
            data=json.dumps({'code': ''}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_submit_code_invalid_json(self, authenticated_client, user, exercise, lesson):
        """Test submitting invalid JSON"""
        # Complete the lesson first
        UserProgress.objects.create(
            user=user,
            lesson=lesson,
            status='completed'
        )
        
        response = authenticated_client.post(
            reverse('coding:submit_code', kwargs={'exercise_id': exercise.id}),
            data='not valid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestGetHintView:
    """Tests for get_hint view"""
    
    def test_get_hint_requires_login(self, client, exercise):
        """Test that get hint requires login"""
        response = client.get(
            reverse('coding:get_hint', kwargs={'exercise_id': exercise.id}) + '?hint_index=0'
        )
        assert response.status_code == 302
    
    def test_get_hint_success(self, authenticated_client, exercise):
        """Test getting a hint"""
        response = authenticated_client.get(
            reverse('coding:get_hint', kwargs={'exercise_id': exercise.id}) + '?hint_index=0'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'hint' in data
    
    def test_get_hint_invalid_index(self, authenticated_client, exercise):
        """Test getting hint with invalid index returns 404"""
        response = authenticated_client.get(
            reverse('coding:get_hint', kwargs={'exercise_id': exercise.id}) + '?hint_index=99'
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data['success'] == False


class TestExerciseModel:
    """Tests for Exercise model"""
    
    def test_exercise_str(self, exercise, lesson):
        """Test exercise string representation"""
        assert str(exercise) == f'{lesson.title} - {exercise.title}'
    
    def test_exercise_difficulty_emoji(self, exercise):
        """Test difficulty emoji"""
        assert exercise.get_difficulty_display_emoji() == '🟢'
        
        exercise.difficulty = 'medium'
        assert exercise.get_difficulty_display_emoji() == '🟡'
        
        exercise.difficulty = 'hard'
        assert exercise.get_difficulty_display_emoji() == '🔴'
    
    def test_exercise_is_solved_by(self, user, exercise):
        """Test is_solved_by method"""
        assert exercise.is_solved_by(user) == False
        
        UserSubmission.objects.create(
            user=user,
            exercise=exercise,
            code='test',
            is_correct=True
        )
        
        assert exercise.is_solved_by(user) == True
    
    def test_exercise_user_attempts(self, user, exercise):
        """Test user_attempts method"""
        assert exercise.user_attempts(user) == 0
        
        UserSubmission.objects.create(
            user=user,
            exercise=exercise,
            code='test1',
            is_correct=False
        )
        
        UserSubmission.objects.create(
            user=user,
            exercise=exercise,
            code='test2',
            is_correct=True
        )
        
        assert exercise.user_attempts(user) == 2


class TestTestCaseModel:
    """Tests for TestCase model"""
    
    def test_test_case_str_visible(self, test_case, exercise):
        """Test visible test case string representation"""
        assert 'Visible' in str(test_case)
    
    def test_test_case_str_hidden(self, exercise, db):
        """Test hidden test case string representation"""
        tc = ExerciseTestCase.objects.create(
            exercise=exercise,
            input_data='{}',
            expected_output='0',
            is_hidden=True,
            order=2
        )
        
        assert 'Hidden' in str(tc)


class TestUserSubmissionModel:
    """Tests for UserSubmission model"""
    
    def test_submission_str_correct(self, user, exercise):
        """Test correct submission string representation"""
        submission = UserSubmission.objects.create(
            user=user,
            exercise=exercise,
            code='test',
            is_correct=True
        )
        
        assert '✓' in str(submission)
    
    def test_submission_str_incorrect(self, user, exercise):
        """Test incorrect submission string representation"""
        submission = UserSubmission.objects.create(
            user=user,
            exercise=exercise,
            code='test',
            is_correct=False
        )
        
        assert '✗' in str(submission)
    
    def test_submission_test_pass_rate(self, user, exercise):
        """Test test pass rate calculation"""
        submission = UserSubmission.objects.create(
            user=user,
            exercise=exercise,
            code='test',
            is_correct=False,
            passed_tests=2,
            total_tests=4
        )
        
        assert submission.test_pass_rate() == 50
    
    def test_submission_test_pass_rate_zero_tests(self, user, exercise):
        """Test test pass rate with zero tests"""
        submission = UserSubmission.objects.create(
            user=user,
            exercise=exercise,
            code='test',
            is_correct=False,
            passed_tests=0,
            total_tests=0
        )
        
        assert submission.test_pass_rate() == 0
