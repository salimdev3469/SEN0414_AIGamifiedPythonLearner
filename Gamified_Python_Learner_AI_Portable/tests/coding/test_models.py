"""
Unit tests for coding models
"""
import pytest
from apps.coding.models import Exercise, TestCase, UserSubmission
from apps.authentication.models import User


@pytest.mark.unit
@pytest.mark.django_db
class TestExerciseModel:
    """Test Exercise model"""
    
    def test_exercise_str_representation(self, test_exercise):
        """Test Exercise __str__ method"""
        str_repr = str(test_exercise)
        assert test_exercise.title in str_repr
        assert test_exercise.lesson.title in str_repr
    
    def test_exercise_get_difficulty_display_emoji(self, test_exercise):
        """Test get_difficulty_display_emoji method"""
        test_exercise.difficulty = 'easy'
        test_exercise.save()
        emoji = test_exercise.get_difficulty_display_emoji()
        assert emoji == '🟢'
        
        test_exercise.difficulty = 'medium'
        test_exercise.save()
        emoji = test_exercise.get_difficulty_display_emoji()
        assert emoji == '🟡'
        
        test_exercise.difficulty = 'hard'
        test_exercise.save()
        emoji = test_exercise.get_difficulty_display_emoji()
        assert emoji == '🔴'
    
    def test_exercise_is_solved_by(self, test_exercise, test_user):
        """Test is_solved_by method"""
        # Initially not solved
        assert test_exercise.is_solved_by(test_user) is False
        
        # Create correct submission
        UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='def add(a, b): return a + b',
            is_correct=True
        )
        
        # Now should be solved
        assert test_exercise.is_solved_by(test_user) is True
    
    def test_exercise_is_solved_by_anonymous(self, test_exercise):
        """Test is_solved_by with anonymous user"""
        from django.contrib.auth.models import AnonymousUser
        anonymous = AnonymousUser()
        assert test_exercise.is_solved_by(anonymous) is False
    
    def test_exercise_user_attempts(self, test_exercise, test_user):
        """Test user_attempts method"""
        # Initially 0 attempts
        assert test_exercise.user_attempts(test_user) == 0
        
        # Create submissions
        UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='code1',
            is_correct=False
        )
        UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='code2',
            is_correct=True
        )
        
        # Should have 2 attempts
        assert test_exercise.user_attempts(test_user) == 2
    
    def test_exercise_user_attempts_anonymous(self, test_exercise):
        """Test user_attempts with anonymous user"""
        from django.contrib.auth.models import AnonymousUser
        anonymous = AnonymousUser()
        assert test_exercise.user_attempts(anonymous) == 0
    
    def test_exercise_default_values(self, test_lesson):
        """Test Exercise default values"""
        exercise = Exercise.objects.create(
            lesson=test_lesson,
            title='Test Exercise',
            description='Test',
            difficulty='easy'
        )
        
        assert exercise.xp_reward == 50
        assert exercise.starter_code == "# Write your code here\n"
        assert exercise.is_published is True
        assert exercise.order == 1


@pytest.mark.unit
@pytest.mark.django_db
class TestTestCaseModel:
    """Test TestCase model"""
    
    def test_testcase_str_representation(self, test_testcase):
        """Test TestCase __str__ method"""
        str_repr = str(test_testcase)
        assert test_testcase.exercise.title in str_repr
        assert 'Test' in str_repr or 'Visible' in str_repr or 'Hidden' in str_repr
    
    def test_testcase_hidden_visibility(self, test_exercise):
        """Test TestCase hidden visibility"""
        hidden_test = TestCase.objects.create(
            exercise=test_exercise,
            input_data='1',
            expected_output='1',
            is_hidden=True
        )
        
        str_repr = str(hidden_test)
        assert 'Hidden' in str_repr


@pytest.mark.unit
@pytest.mark.django_db
class TestUserSubmissionModel:
    """Test UserSubmission model"""
    
    def test_usersubmission_str_representation(self, test_user, test_exercise):
        """Test UserSubmission __str__ method"""
        submission = UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='def add(a, b): return a + b',
            is_correct=True
        )
        
        str_repr = str(submission)
        assert test_user.username in str_repr
        assert test_exercise.title in str_repr
        assert 'Correct' in str_repr or '✓' in str_repr
    
    def test_usersubmission_str_incorrect(self, test_user, test_exercise):
        """Test UserSubmission __str__ for incorrect submission"""
        submission = UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='def add(a, b): return a - b',
            is_correct=False
        )
        
        str_repr = str(submission)
        assert 'Incorrect' in str_repr or '✗' in str_repr
    
    def test_usersubmission_test_pass_rate(self, test_user, test_exercise):
        """Test test_pass_rate method"""
        submission = UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='code',
            passed_tests=3,
            total_tests=5
        )
        
        pass_rate = submission.test_pass_rate()
        assert pass_rate == 60  # 3/5 * 100
    
    def test_usersubmission_test_pass_rate_zero(self, test_user, test_exercise):
        """Test test_pass_rate with zero total tests"""
        submission = UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='code',
            passed_tests=0,
            total_tests=0
        )
        
        pass_rate = submission.test_pass_rate()
        assert pass_rate == 0
    
    def test_usersubmission_test_pass_rate_100(self, test_user, test_exercise):
        """Test test_pass_rate with 100% pass rate"""
        submission = UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='code',
            passed_tests=5,
            total_tests=5
        )
        
        pass_rate = submission.test_pass_rate()
        assert pass_rate == 100
    
    def test_usersubmission_ordering(self, test_user, test_exercise):
        """Test UserSubmission ordering by submitted_at"""
        submission1 = UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='code1'
        )
        
        import time
        time.sleep(0.01)  # Small delay to ensure different timestamps
        
        submission2 = UserSubmission.objects.create(
            user=test_user,
            exercise=test_exercise,
            code='code2'
        )
        
        # Latest should be first
        submissions = UserSubmission.objects.all()
        assert submissions[0] == submission2

